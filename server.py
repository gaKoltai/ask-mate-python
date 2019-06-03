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
    searched_question = {}
    searched_answers = []
    if question_id is not None:
        questions = connection.get_info_from_file(connection.QUESTION_FILE)

        for question in questions:
            if question['id'] == str(question_id):
                for item, value in question.items():
                    searched_question[item] = value
        answers = connection.get_info_from_file(connection.ANSWER_FILE)
        for answer in answers:
            if answer['question_id'] == str(question_id):
                searched_answers.append(answer)
        #question = data_manager.get_question_by_id(question_id)
        #answers = data_manager.get_answers_by_question_id(question_id)
    return render_template('question_with_answers.html', question=searched_question, answers=searched_answers)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )