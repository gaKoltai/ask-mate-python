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


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )