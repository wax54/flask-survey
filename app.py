from flask import Flask, render_template as render, request, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

#debugger stuff
#import pdb
# pdb.set_trace()


#make the app
app = Flask(__name__)

#For the debugger toolbar
app.config['SECRET_KEY'] = 'a secret key'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)


@app.route('/')
def index():
    return render('survey_start.html', survey=survey)


@app.route('/start_survey', methods=["POST"])
def survey_start():
    session['responses'] = []
    return redirect('questions/0')


@app.route('/questions/<int:q_id>')
def question(q_id):
    curr_question = len(session['responses'])
    #not the right question
    if q_id != curr_question:
        flash("let's not try to make trouble here. Let's just finish the suvery ok?")
        return redirect(f"/questions/{curr_question}")
    
    #all q's are answered - The end of the survey
    if len(survey.questions) <= curr_question:
        return redirect('/thankyou')
    
    #try to get the question
    try:
        question = survey.questions[q_id]
        return render('question.html', question=question, title=survey.title)
    except:
        return redirect('/')

@app.route('/answer', methods=["POST"])
def answer():
    curr_question = len(session['responses'])
    
    answer = request.form.get('choice')
    if not answer:
        flash("Please answer the Question!!!")
        return redirect(f"/questions/{curr_question}")
    
    responses = session['responses']
    responses.append(answer)
    session['responses'] = responses
    curr_question = len(session['responses'])
    return redirect(f"/questions/{curr_question}")

@app.route('/thankyou')
def thankyou_page():
    return render('thankyou.html')