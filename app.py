from flask import Flask, render_template as render, request, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

#debugger stuff
#import pdb
# pdb.set_trace()


#make the app
app = Flask(__name__)

#For the debugger toolbar
app.config['SECRET_KEY'] = 'a secret key'
toolbar = DebugToolbarExtension(app)

#responses
responses = []
curr_question = 0


@app.route('/')
def survey_start():
    return render('survey_start.html', survey=survey)

@app.route('/questions/<int:q_id>')
def question(q_id):
    #not the right question
    if q_id != curr_question:
        flash("let's not try to make trouble here. Let's just finish the suvery ok?")
        return redirect(f"/questions/{curr_question}")
    
    #all q's are answered the end of the survey
    if len(survey.questions) <= len(responses):
        return redirect('/thankyou')
    #try to get the question
    try:
        question = survey.questions[q_id]
        return render('question.html', question=question, title=survey.title)
    except:
        return redirect('/')

@app.route('/answer', methods=["POST"])
def answer():
    global curr_question
    
    res = request.form.get('choice')
    if not res:
        flash("Please answer the Question!!!")
        return redirect(f"/questions/{curr_question}")
    responses.append(res)
    curr_question = len(responses)
    return redirect(f"/questions/{curr_question}")

@app.route('/thankyou')
def thankyou_page():
    return render('thankyou.html')