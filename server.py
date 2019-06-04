from flask import Flask, render_template, request, redirect, url_for
import connection
import data_manager

app = Flask(__name__)


@app.route('/')
def route_list():
    user_questions = connection.get_info_from_file(connection.QUESTION_FILE)
    data_manager.add_line_breaks_to_data(user_questions)
    data_manager.get_post_time(user_questions)
    return render_template('list.html', user_questions =user_questions)


@app.route('/question/<int:question_id>')
def route_question_with_answer(question_id=None):
    if question_id is not None:
        question = data_manager.get_question_by_id(question_id)
        answers = data_manager.get_answers_by_question_id(question_id)
    return render_template('question_with_answers.html', question=question, answers=answers)


@app.route('/question/<int:question_id>/new-answer', methods=['GET', 'POST'])
def route_new_answer(question_id=None):
    if request.method == 'POST':
        answer = request.form.get('message')
        data_manager.add_answer(question_id, answer)
        return redirect(f'/question/{question_id}')
    if question_id is not None:
        question = data_manager.get_question_by_id(question_id)
    return render_template('add_answer.html', question=question)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )