from flask import Flask, render_template as render, request, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

# debugger stuff
# import pdb
# pdb.set_trace()

SURVEY_KEY = "survey_name"
RES_KEY = "responses"


# make the app
app = Flask(__name__)

# For the debugger toolbar
app.config['SECRET_KEY'] = 'a secret key'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)


@app.route('/')
def survey_picking_page():
    """The page that allows the user to pick a survey to complete"""
    return render('survey_picking_page.html', surveys=surveys)


@app.route('/<survey_name>')
def survey_start_page(survey_name):
    """the start page for a specific survey"""
    survey = surveys.get(survey_name)
    if survey:
        return render('survey_start.html', survey=survey, survey_name=survey_name)
    return redirect('/')


@app.route('/start_survey/<survey_name>', methods=["POST"])
def survey_start(survey_name):
    """starts a session for the survey and navigates to the first question"""
    session[SURVEY_KEY] = survey_name
    session[RES_KEY] = []
    return redirect('/questions/0')


@app.route('/questions/<int:q_id>')
def question(q_id):
    """Displays the question"""
    curr_question = len(session[RES_KEY])
    survey = surveys.get(session[SURVEY_KEY])
    # not the right question
    if q_id != curr_question:
        flash("let's not try to make trouble here. Let's just finish the suvery ok?")
        return redirect(f"/questions/{curr_question}")

    # all q's are answered - The end of the survey
    if len(survey.questions) <= curr_question:
        return redirect('/thankyou')

    # try to get the question
    try:
        question = survey.questions[q_id]
        return render('question.html', question=question, title=survey.title)
    except:
        return redirect('/')


@app.route('/answer', methods=["POST"])
def answer():
    """records an answer if present"""
    curr_question = len(session[RES_KEY])

    answer = request.form.get('choice')
    if not answer:
        flash("Please answer the Question!!!")
        return redirect(f"/questions/{curr_question}")

    responses = session[RES_KEY]
    responses.append(answer)
    session[RES_KEY] = responses
    curr_question = len(session[RES_KEY])
    return redirect(f"/questions/{curr_question}")


@app.route('/thankyou')
def thankyou_page():
    """shows user the thank you page"""
    return render('thankyou.html', results=get_q_and_a())


def get_q_and_a():
    """formats the questions and answers as a list of tuples
    for as many questions as there are in th current sessions survey. 
    all non-answered questions will be None
        [(q1,a1),(q2,a2)...]
    """
    # import pdb
    # pdb.set_trace()
    survey = surveys.get(session[SURVEY_KEY])
    answers = session[RES_KEY]
    q_and_a = []
    for i in range(len(survey.questions)):
        a = answers[i] if i < len(answers) else None
        q = survey.questions[i].question
        q_and_a.append((q, a))
    return q_and_a
