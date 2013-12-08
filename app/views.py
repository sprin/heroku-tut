# -*- coding: utf-8 -*-
from flask import render_template, request, flash, jsonify
from utils import s3_upload, test_conn, insert_file_upload
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
    destination = s3_upload(f)

    # Run word count on the file content
    f.seek(0)
    word_counts = count_words(f.read())

    # Insert counts into DB
    insert_file_upload(
        document_name = document_name,
        filename = f.filename,
        word_counts = word_counts,
    )

    flash('"{document_name}" uploaded to S3 as <a href="{dst}">{dst}</a>'.format(
        document_name=document_name,
        dst=destination,
    ))
    return render_template('index.html')

@app.route('/wordcloud/', methods=['GET'])
def word_cloud():
    return render_template('word_cloud.html')

@app.route('/test_connection', methods=['GET'])
def test_connection():
    """
    Insert a fake record into the database and return the values of the
    newly created row (using RETURNING).
    """
    return jsonify(result=test_conn())

