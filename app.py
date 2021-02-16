from flask import Flask, render_template as render, request
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey

app = Flask(__name__)

app.config['SECRET_KEY'] = 'a secret key'
toolbar = DebugToolbarExtension(app)
responses = []

@app.route('/')
def survey_start():
    return render('survey_start.html', survey=satisfaction_survey)