from flask import Flask, render_template, request, redirect, url_for
import connection
import data_manager
import util

app = Flask(__name__)


@app.route('/', methods = ['POST', 'GET'])
@app.route('/list', methods = ['POST', 'GET'])
def route_questions(vote = None, id=None):
    if request.method == 'GET':
        user_questions = connection.get_info_from_file(connection.QUESTION_FILE)
        data_manager.add_line_breaks_to_data(user_questions)
        user_questions = data_manager.sort_data(user_questions, request.args.get('order_by'),
                                                request.args.get('order_direction'))
        data_manager.get_post_time(user_questions)
        return render_template('list.html', user_questions =user_questions, order_by = request.args.get('order_by'),
                               order_direction=request.args.get('order_direction'))
    if request.method == 'POST':
        if vote:
            data_manager.vote(vote, id)
            return redirect(url_for('route_questions'))
        else:
            return redirect(url_for('route_questions', order_by = request.form['order_by'], order_direction = request.form['order_direction']))


@app.route('/question/<int:question_id>')
def route_question_with_answer(question_id=None):
    if question_id is not None:
        question = data_manager.get_question_by_id(question_id)
        answers = data_manager.get_answers_by_question_id(question_id)
    return render_template('question_with_answers.html', question=question, answers=answers, question_id=question_id)


@app.route('/add-question', methods=['GET', 'POST'])
def route_ask_new_question():

    if request.method == 'POST':

        new_question = data_manager.new_question_entry(request.form)
        connection.pass_user_story_to_file(new_question, connection.QUESTION_FILE, connection.QUESTION_HEADER)

        return redirect(url_for(route_question_with_answer, question_id=new_question['id']))

    return render_template('new_question.html')


@app.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def route_edit_question(question_id):

    question = data_manager.get_answers_by_question_id(question_id)

    if request.method == 'POST':

        questions_with_edit = data_manager.edit_question(request.form, question)
        connection.write_data_to_file(connection.QUESTION_FILE, connection.QUESTION_HEADER, questions_with_edit)

        return redirect(url_for(route_question_with_answer, question_id=question['id']))


    return render_template('edit_question.html', question=question)


@app.route('/question/<int:question_id>/<vote>')
def route_vote(question_id=None, vote = None):
    data_manager.vote(question_id, vote)
    return redirect(url_for('route_questions'))


@app.route('/question/<int:question_id>/new-answer', methods=['GET', 'POST'])
def route_new_answer(question_id=None):
    if request.method == 'POST':
        answer = request.form.get('answer')
        data_manager.add_answer(question_id, answer)
        return redirect(url_for('route_question_with_answer', question_id=question_id))
    question = data_manager.get_question_by_id(question_id)
    return render_template('add_answer.html', question=question, question_id=question_id)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )