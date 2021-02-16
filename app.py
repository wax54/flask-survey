from flask import Flask, render_template as render, request
from flask_debugtoolbar import flask_debugtoolbar

app = Flask(__name__)
app.config['secret_key'] = 'a secret key'
responses = []