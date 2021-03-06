import json
import os
import re
from unicodedata import normalize

import boto
from uuid import uuid4
from werkzeug import secure_filename

from app import app
import tables
from tables import result_as_list_of_dicts
from amqp_connection import get_amqp_connection


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def s3_upload(source_file,acl='public-read'):
    source_filename = secure_filename(source_file.filename)
    source_extension = os.path.splitext(source_filename)[1]

    destination_filename = uuid4().hex + source_extension

    # Connect to S3
    conn = boto.connect_s3(app.config["S3_KEY"], app.config["S3_SECRET"])
    bucket_name = app.config["S3_BUCKET"]
    b = conn.get_bucket(bucket_name)

    key = "/".join([
        app.config["S3_UPLOAD_DIRECTORY"],
        destination_filename,
    ])

    # Upload the File
    sml = b.new_key(key)
    sml.set_contents_from_string(source_file.read())

    # Set the file's permissions.
    sml.set_acl(acl)

    # Return the key to the file
    return key

def get_s3_path(key):
    return "{loc}{bucket_name}/{key}".format(
        loc = app.config["S3_LOCATION"],
        bucket_name = app.config["S3_BUCKET"],
        key = key,
    )

def test_conn():
    return insert_file_upload_meta(
        document_name = 'Fake Document',
        document_slug = 'fake_document',
        s3_key = 'files/does_not_exist.txt',
        filename = 'does_not_exist.txt',
    )

def insert_file_upload_meta(
    document_name = None,
    document_slug = None,
    s3_key = None,
    filename = None,
):
    if None in [document_name, document_slug, s3_key, filename]:
        return ValueError('missing required named params')

    t = tables.reflected['file_upload_meta']
    query = (
        t
        .insert()
        .values(
            document_name = document_name,
            document_slug = document_slug,
            s3_key = s3_key,
            filename = filename,
        )
        .returning(
            t.c.document_name,
            t.c.document_slug,
            t.c.s3_key,
            t.c.time_uploaded,
            t.c.filename,
        )
    )
    result = result_as_list_of_dicts(query)[0]
    return result

def fetch_file_upload_meta(document_slug):
    t = tables.reflected['file_upload_meta']
    query = (
        t
        .select()
        .where(
            t.c.document_slug == document_slug
        )
        .order_by(
            t.c.time_uploaded.desc()
        )
    )
    result = result_as_list_of_dicts(query)
    if result:
        return result[0]
    else:
        return {
            'document_name': 'Error',
            'word_counts': {
                'error': 5,
                'nosuch': 3,
                'document': 2,
                'name': 1
            }
        }


def slugify(text, delim=u'-'):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))

def put_doc_on_queue(
    document_slug = None,
    time_uploaded = None,
    s3_key = None,
):
    if None in [document_slug, time_uploaded, s3_key]:
        return ValueError('missing required named params')
    connection = get_amqp_connection()
    channel = connection.channel() # start a channel
    channel.queue_declare(queue='countwords') # Declare a queue
    msg = json.dumps({
        'document_slug': document_slug,
        'time_uploaded': time_uploaded.isoformat(),
        's3_key': s3_key,
    })
    channel.basic_publish(exchange='', routing_key='countwords', body=msg)

