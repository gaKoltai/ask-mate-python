import connection
from time import asctime, localtime
import util
import os
from werkzeug.utils import secure_filename
from server import app


def get_post_time(user_data):
    for data in user_data:
        for header, info in data.items():
            if header == 'submission_time':
                data[header] = asctime(localtime(int(info)))

    return user_data


def sort_data(data, order_by, order_direction):
    is_reversed = False if order_direction == "asc" else True
    order_by = order_by if order_by else 'submission_time'
    if order_by == 'id' or order_by == 'view_number' or order_by == 'vote_number' or order_by == 'submission_time':
        return sorted(data, key=lambda item: int(item[order_by]), reverse=is_reversed)
    else:
        return sorted(data, key=lambda item: item[order_by], reverse=is_reversed)


def vote(item_id, up_or_down, q_or_a):
    if q_or_a == "question":
        f = connection.QUESTION_FILE
        header = connection.QUESTION_HEADER
    else:
        f = connection.ANSWER_FILE
        header = connection.ANSWER_HEADER

    items = connection.get_info_from_file(f)
    for item in items:
        if item_id == int(item['id']):
            item['vote_number'] = int(item['vote_number'])
            item['vote_number'] += 1 if up_or_down == "vote-up" else -1
            item['vote_number'] = str(item['vote_number'])
    connection.write_data_to_file(f, header, items)


def increment_view_number(item_id):
    question = get_question_by_id(item_id)
    question['view_number'] = str(int(question['view_number'])+1)
    questions = edit_question(question, item_id)
    connection.write_data_to_file(connection.QUESTION_FILE, connection.QUESTION_HEADER, questions)


def add_line_breaks_to_data(user_data):
    for data in user_data:
        for header, info in data.items():
            if type(info) == str:
                data[header] = info.replace('\n', '<br>')

    return user_data


def get_question_by_id(question_id):
    searched_question = {}
    questions = connection.get_info_from_file(connection.QUESTION_FILE)
    for question in questions:
        if question['id'] == str(question_id):
            for item, value in question.items():
                searched_question[item] = value
    return searched_question


def get_answers_by_question_id(question_id):
    searched_answers = []
    answers = connection.get_info_from_file(connection.ANSWER_FILE)
    get_post_time(answers)
    for answer in answers:
        if answer['question_id'] == str(question_id):
            searched_answers.append(answer)
    return searched_answers


def get_new_id(file_name):

    new_id = max((int(data['id']) for data in connection.get_info_from_file(file_name))) + 1

    return new_id


def add_question(entry_data, image_name):

    if image_name == '':
        image_path = ''

    else:
        image_path = f'{connection.UPLOAD_FOLDER}/{image_name}'

    new_entry = {'id':get_new_id(connection.QUESTION_FILE),
                 'submission_time':util.get_local_time(),
                 'view_number':0,
                 'vote_number': 0,
                 'image': image_path}

    for header, data in entry_data.items():
        new_entry[header] = data

    return new_entry


def edit_question(edited_info, question_id):
    questions = connection.get_info_from_file(connection.QUESTION_FILE)
    for question in questions:
        if question['id'] == str(question_id):
            for header, info in edited_info.items():
                question[header] = edited_info[header]

    return questions


def add_answer(question_id, answer, image_name):

    if image_name == '':
        image_path = ''
    else:
        image_path = f'{connection.UPLOAD_FOLDER}/{image_name}'

    answers = connection.get_info_from_file(connection.ANSWER_FILE)
    new_answer = {'id': get_new_id(connection.ANSWER_FILE),
                  'submission_time': util.get_local_time(),
                  'vote_number': 0,
                  'question_id': question_id,
                  'message': answer,
                  "image": image_path}

    answers.append(new_answer)
    connection.write_data_to_file(connection.ANSWER_FILE, connection.ANSWER_HEADER, answers)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in connection.ALLOWED_FILE_EXTENSIONS


def upload_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


def delete_answer_by_answer_id(answer_id):
    answers = connection.get_info_from_file(connection.ANSWER_FILE)
    for answer in answers:
        if answer['id'] == str(answer_id):
            answers.remove(answer)
            try:
                os.remove(answer['image'])
            except FileNotFoundError:
                pass
    connection.write_data_to_file(connection.ANSWER_FILE, connection.ANSWER_HEADER, answers)


def get_question_id_by_answer_id(answer_id):
    answers = connection.get_info_from_file(connection.ANSWER_FILE)
    question_id = None
    for answer in answers:
        if answer['id'] == str(answer_id):
            question_id = int(answer['question_id'])
    return question_id


def delete_question(question_id):
    questions = connection.get_info_from_file(connection.QUESTION_FILE)
    for question in questions:
        if question['id'] == str(question_id):
            questions.remove(question)
            searched_answers = get_answers_by_question_id(question['id'])
            for answer in searched_answers:
                delete_answer_by_answer_id(answer['id'])
            try:
                os.remove(question['image'])
            except FileNotFoundError:
                pass
    connection.write_data_to_file(connection.QUESTION_FILE, connection.QUESTION_HEADER, questions)
