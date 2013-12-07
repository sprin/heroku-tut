# -*- coding: utf-8 -*-
import os

from flask import render_template

from app import app

@app.route('/')
def index():
    me = os.environ.get('ME')
    context = {
        'hi_from': me,
    }
    return render_template('index.html', **context)

