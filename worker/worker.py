import datetime
import json
import os
import psycopg2
import pika
import urlparse
import urllib2

from word_count import count_words

DB_CONN_URI = os.environ['DATABASE_URL']
AMQP_URI= urlparse.urlparse(os.environ['CLOUDAMQP_URL'])


amqp_params = pika.ConnectionParameters(
    host=AMQP_URI.hostname,
    virtual_host=AMQP_URI.path[1:],
    credentials=pika.PlainCredentials(
        AMQP_URI.username,
        AMQP_URI.password,
    ))

def get_psycopg2_connection():
   return psycopg2.connect(DB_CONN_URI)

def update_file_upload_meta(
    document_slug = None,
    time_uploaded = None,
    word_counts = None,
):
    if None in [document_slug, time_uploaded, word_counts]:
        return ValueError('missing required named params')
    conn = get_psycopg2_connection()
    cur = conn.cursor()
    cur.execute(
'''
UPDATE file_upload_meta
SET word_counts = %(word_counts)s
WHERE
    document_slug = %(document_slug)s
    AND time_uploaded = %(time_uploaded)s
'''
    , {
        'word_counts': word_counts,
        'document_slug': document_slug,
        'time_uploaded': time_uploaded,
    }
    )
    conn.commit()
    conn.close()

def get_amqp_connection():
    return pika.BlockingConnection(amqp_params)

def get_s3_path(key):
    return "{loc}{bucket_name}/{key}".format(
        loc = os.environ["S3_LOCATION"],
        bucket_name = os.environ["S3_BUCKET"],
        key = key,
    )

def start_consuming():
    connection = get_amqp_connection()
    channel = connection.channel() # start a channel
    channel.queue_declare(queue='countwords') # Declare a queue

    # create a function which is called on incoming messages
    def callback(ch, method, properties, body):
        print " [x] Received %r" % (body)
        document_meta = json.loads(body)
        start = datetime.datetime.now()


        print '     Fetching from S3'
        s3_key = document_meta['s3_key']
        s3_path = get_s3_path(s3_key)
        response = urllib2.urlopen(s3_path)
        text_blob = response.read()

        word_count = count_words(text_blob)

        update_file_upload_meta(
            document_slug = document_meta['document_slug'],
            time_uploaded = document_meta['time_uploaded'],
            word_counts = json.dumps(word_count),
        )
        duration = datetime.datetime.now() - start
        print '     Done in {0}!'.format(duration)

    # set up subscription on the queue
    channel.basic_consume(callback,
        queue='countwords',
        no_ack=True)

    channel.start_consuming() # start consuming (blocks)

    connection.close()

if __name__ == '__main__':
    start_consuming()
