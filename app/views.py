# -*- coding: utf-8 -*-
import json
from flask import (
    render_template,
    request,
    flash,
    jsonify,
)
from utils import (
    s3_upload,
    get_s3_path,
    test_conn,
    insert_file_upload_meta,
    fetch_file_upload_meta,
    slugify,
    put_doc_on_queue,
)
from word_count import count_words

from app import app

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def handle_upload():
    document_name = request.form['document-name']
    f = request.files['input-file']

    # Upload to S3 synchronously
    s3_key = s3_upload(f)

    # Create slug for document
    document_slug = slugify(document_name)

    # Insert counts into DB
    upload_meta = insert_file_upload_meta(
        document_name = document_name,
        document_slug = document_slug,
        s3_key = s3_key,
        filename = f.filename,
    )

    put_doc_on_queue(
        document_slug = document_slug,
        time_uploaded = upload_meta['time_uploaded'],
        s3_key = s3_key,
    )

    flash(
        '"{document_name}" uploaded to S3 as <a href="{dst}">{dst}</a>'
        '<br><br>Check out your word cloud at '
        '<a href="/wordcloud/{slug}">{base}wordcloud/{slug}</a>!'
        .format(
            document_name = document_name,
            dst = get_s3_path(s3_key),
            slug = document_slug,
            base = request.base_url,
    ))
    return render_template('index.html')

@app.route('/wordcloud/<document_slug>', methods=['GET'])
def word_cloud(document_slug):
    meta= fetch_file_upload_meta(document_slug)
    bootstrapped = {
        'word_counts': meta['word_counts'],
    }
    ctx = {
        'bootstrapped': json.dumps(bootstrapped),
        'document_name': meta['document_name'],
    }
    return render_template('word_cloud.html', **ctx)

@app.route('/test_connection', methods=['GET'])
def test_connection():
    """
    Insert a fake record into the database and return the values of the
    newly created row (using RETURNING).
    """
    return jsonify(result=test_conn())

