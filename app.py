from flask import Flask, render_template as render, request, redirect, flash, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

# debugger stuff
# import pdb
# pdb.set_trace()

SURVEY_KEY = "survey_id"
RES_KEY = "responses"
TEMP_SURVEY = "temp_survey"

# make the app
app = Flask(__name__)

# For the debugger toolbar
app.config['SECRET_KEY'] = 'a secret key'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# toolbar = DebugToolbarExtension(app)


@app.route('/')
def survey_picking_page():
    """The page that allows the user to pick a survey to complete"""
    surveys = split_surveys()
    return render('survey_picking_page.html', valid_surveys=surveys['valid'], done_surveys=surveys['done'])


@app.route('/', methods=["POST"])
def survey_start_page():
    """the start page for a specific survey"""

    survey_id = request.form['survey_id']
    survey = surveys.get(survey_id)

    # if the survey exists...
    if survey:
        # ...show the user the survey info
        return render('survey_start.html', survey=survey, survey_id=survey_id)
    # ...otherwise, navigate them back to the pick a survey page
    return redirect('/')


@app.route('/start_survey', methods=["POST"])
def survey_start():
    """starts a session for the survey and navigates to the first question"""
    session.permanent = True
    # store the survey name
    session[SURVEY_KEY] = request.form['survey_id']
    # make a new responses list in the session
    session[session[SURVEY_KEY] + RES_KEY] = []
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
    # there is no survey/response object rn...
    if responses is False:
        #... return to the home page
        return redirect('/')
    # gets the current question
    curr_question = len(responses)
    # gets the answer from the POST data
    answer = request.form.get('choice')
    # if the user didn't select an answer...
    if answer == None:
        # flash them and send them back to the same question
        flash("Please answer the Question!!!")
        return redirect(f"/questions/{curr_question}")

    extra_info = request.form.get('extra_info')
    if extra_info == None:
        extra_info = ''
    # append the response
    responses.append((answer, extra_info))
    # store it back in the session
    session[session[SURVEY_KEY]+RES_KEY] = responses
    # move the user on to the next question
    curr_question = len(responses)
    return redirect(f"/questions/{curr_question}")


@app.route('/thankyou')
def thankyou_page():
    """shows user the thank you page"""
    # if the survey is really over...
    if survey_over():
        # send them the thankyou page
        return render('thankyou.html', results=get_q_and_a(), survey_id=session[SURVEY_KEY])
    # otherwise, give 'em back to questions to deal with...
    return redirect('/questions/0')


@app.route('/get_results', methods=["GET"])
def review_previous_survey():
    """starts a session for the survey and navigates to the first question"""
    # store the survey name
    session[SURVEY_KEY] = request.args['survey_id']
    return redirect('/thankyou')


def get_q_and_a():
    """formats the questions and answers as a list of tuples
    for as many questions as there are in th current sessions survey. 
    all non-answered questions will be None
    returns False when no session[SURVEY_KEY] is present
        [(q1,a1),(q2,a2)...]
    """
    survey = get_survey()
    responses = get_responses()
    if not survey or not responses:
        # no survey in session, return false
        return False
    q_and_a = []
    for i in range(len(survey.questions)):
        # emulates get of a dictionary
        response = responses[i] if i < len(responses) else (None, '')
        a, extra_info = response
        # gets the question from the survey
        q = survey.questions[i].question
        # throws 'em together
        q_and_a.append((q, a, extra_info))
    return q_and_a


def survey_over():
    """checks to see if the survey is over
    returns Flase if no survey in session
    """
    if not get_survey():
        # no survey in session, return false
        return False

    curr_question = len(get_responses())
    survey_length = len(get_survey().questions)
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
    if not session.get(SURVEY_KEY):
        return False
    if session.get(session[SURVEY_KEY]+RES_KEY) == None:
        return False
    return session[session[SURVEY_KEY]+RES_KEY]


def split_surveys():
    split_surveys = {"done":  {},  "valid":  {}}
    for survey_id, survey in surveys.items():
        # If the key exists...
        if session.get(survey_id+RES_KEY):
            # ... add it to the done surveys
            split_surveys['done'][survey_id] = survey
        else:
            # ...add it to the valid responses
            split_surveys['valid'][survey_id] = survey
    return split_surveys
