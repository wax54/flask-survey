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
# toolbar = DebugToolbarExtension(app)


@app.route('/')
def survey_picking_page():
    """The page that allows the user to pick a survey to complete"""
    return render('survey_picking_page.html', surveys=surveys)


@app.route('/<survey_name>')
def survey_start_page(survey_name):
    """the start page for a specific survey"""
    survey = surveys.get(survey_name)
    # if the survey exists...
    if survey:
        # ...show the user the survey info
        return render('survey_start.html', survey=survey, survey_name=survey_name)
    # ...otherwise, navigate them back to the pick a survey page
    return redirect('/')


@app.route('/start_survey/<survey_name>', methods=["POST"])
def survey_start(survey_name):
    """starts a session for the survey and navigates to the first question"""
    # store the survey name
    session[SURVEY_KEY] = survey_name
    # make a new responses list in the session
    session[RES_KEY] = []
    return redirect('/questions/0')


@app.route('/questions/<int:q_id>')
def question(q_id):
    """Displays the question"""

    # get the survey from surveys using the survey name
    survey = get_survey()
    responses = get_responses()
    if survey == False or responses == False:
        # no survey in session, go to the survey picker
        return redirect('/')

    # get the current question index
    curr_question = len(responses)

    # if the survey is over
    if survey_over():
        # send them to the thankyou page
        return redirect('/thankyou')

    # if the user is trying to access a question out of order...
    if q_id != curr_question:
        # ...flash 'em and send them to the right Q
        flash("let's not try to make trouble here. Just finish the suvery ok?")
        return redirect(f"/questions/{curr_question}")

    # try to get the question
    try:
        question = survey.questions[q_id]
        return render('question.html', question=question, title=survey.title)
    except:
        return redirect('/')


@app.route('/answer', methods=["POST"])
def answer():
    """records an answer if present"""
    responses = get_responses()
    # gets the current question
    curr_question = len(responses)
    # gets the answer from the POST data
    answer = request.form.get('choice')
    # if the user didn't select an answer...
    if answer == None:
        # flash them and send them back to the same question
        flash("Please answer the Question!!!")
        return redirect(f"/questions/{curr_question}")
    # append the response
    responses.append(answer)
    # store it back in the session
    session[RES_KEY] = responses
    # move the user on to the next question
    curr_question = len(responses)
    return redirect(f"/questions/{curr_question}")


@app.route('/thankyou')
def thankyou_page():
    """shows user the thank you page"""
    # if the survey is really over...
    if survey_over():
        # send them the thankyou page
        return render('thankyou.html', results=get_q_and_a())
    # otherwise, give 'em back to questions to deal with...
    return redirect('/questions/0')


def get_q_and_a():
    """formats the questions and answers as a list of tuples
    for as many questions as there are in th current sessions survey. 
    all non-answered questions will be None
    returns False when no session[SURVEY_KEY] is present
        [(q1,a1),(q2,a2)...]
    """
    survey = get_survey()
    answers = session[RES_KEY]
    if not survey or not answers:
        # no survey in session, return false
        return False
    q_and_a = []
    for i in range(len(survey.questions)):
        # emulates get of a dictionary
        a = answers[i] if i < len(answers) else None
        # gets the question from the survey
        q = survey.questions[i].question
        # throws 'em together
        q_and_a.append((q, a))
    return q_and_a


def survey_over():
    """checks to see if the survey is over
    returns Flase if no survey in session
    """
    if not get_survey():
        # no survey in session, return false
        return False

    curr_question = len(session[RES_KEY])
    survey_length = len(surveys.get(session[SURVEY_KEY]).questions)
    # this means all q's are answered
    # (and maybe more, lol I wonder if that'll ever happen...)
    # - it's the end of the survey
    if survey_length <= curr_question:
        return True
    return False


def get_survey():
    """gets the survey from the session"""
    if session.get(SURVEY_KEY) == None:
        return False
    return surveys.get(session[SURVEY_KEY])


def get_responses():
    """Gets the responses from the session"""
    if session.get(RES_KEY) == None:
        return False
    return session[RES_KEY]
