# -*- coding: utf-8 -*-
from flask import render_template, request, flash, jsonify
from utils import s3_upload, test_conn
from tables import reflect_database

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

    flash('"{document_name}" uploaded to S3 as <a href="{dst}">{dst}</a>'.format(
        document_name=document_name,
        dst=destination,
    ))
    return render_template('index.html')

@app.route('/test_connection', methods=['GET'])
def test_connection():
    """
    Insert a fake record into the database and return the values of the
    newly created row (using RETURNING).
    """
    return jsonify(result=test_conn())

