# -*- coding: utf-8 -*-
from flask import render_template, request
from utils import s3_upload

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

    resp = '"{document_name}" uploaded to S3 as {dst}'.format(
        document_name=document_name,
        dst=destination,
    )
    return resp
