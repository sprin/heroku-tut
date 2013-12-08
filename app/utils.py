import json
import os
import re
from unicodedata import normalize

import boto
from sqlalchemy import select
from uuid import uuid4
from werkzeug import secure_filename

from app import app
import tables
from tables import result_as_list_of_dicts


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

    # Return the HTTP path to the file
    path = "{loc}{bucket_name}/{key}".format(
        loc = app.config["S3_LOCATION"],
        bucket_name = bucket_name,
        key = key,
    )

    return path

def test_conn():
    return insert_file_upload_meta(
        document_name = 'Fake Document',
        filename = 'does_not_exist.txt',
        word_counts = {},
    )

def insert_file_upload_meta(
    document_name = None,
    document_slug = None,
    filename = None,
    word_counts = None
):
    if None in [document_name, document_slug, filename, word_counts]:
        return ValueError('missing required named params')

    t = tables.reflected['file_upload_meta']
    query = (
        t
        .insert()
        .values(
            document_name = document_name,
            document_slug = document_slug,
            filename = filename,
            word_counts = json.dumps(word_counts),
        )
        .returning(
            t.c.document_name,
            t.c.document_slug,
            t.c.time_uploaded,
            t.c.filename,
            t.c.word_counts,
        )
    )
    result = result_as_list_of_dicts(query)
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

