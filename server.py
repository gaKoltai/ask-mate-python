from flask import Flask, render_template, request, redirect, url_for
import connection
import data_manager
import util

app = Flask(__name__)


@app.route('/', methods = ['POST', 'GET'])
def route_questions(vote = None, id=None):
    if request.method == 'GET':
        user_questions = connection.get_info_from_file(connection.QUESTION_FILE)
        data_manager.add_line_breaks_to_data(user_questions)
        data_manager.get_post_time(user_questions)
        return render_template('list.html', user_questions =user_questions)
    if request.method == 'POST':
        if vote:
            data_manager.vote(vote, id)
            return redirect(url_for('route_questions'))


@app.route('/question/<int:question_id>')
def route_question_with_answer(question_id=None):
    if question_id is not None:
        question = data_manager.get_question_by_id(question_id)
        answers = data_manager.get_answers_by_question_id(question_id)
    return render_template('question_with_answers.html', question=question, answers=answers)

@app.route('/ask-question', methods=['GET', 'POST'])
def route_ask_new_question():

    question = {}
    id = data_manager.get_new_id(connection.QUESTION_FILE)
    post_time = util.get_local_time()

    if request.method == 'POST':

        for header, info in request.form.items():
            question[header] = info

        connection.pass_user_story_to_file(question, connection.QUESTION_FILE, connection.QUESTION_HEADER)

        return redirect('/')

    return render_template('new_question.html', id= id, time=post_time)


@app.route('/question/<int:question_id>/<vote>')
def route_vote(question_id=None, vote = None):
    data_manager.vote(question_id, vote)
    return redirect(url_for('route_questions'))


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )