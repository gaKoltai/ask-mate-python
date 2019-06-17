import connection
from datetime import datetime
import util
import os
from werkzeug.utils import secure_filename
from psycopg2 import sql


@connection.connection_handler
def get_data_from_db(cursor, table):

    cursor.execute(
        sql.SQL("SELECT * FROM {table}").format(table=sql.Identifier(table))
    )

    data = cursor.fetchall()

    return data

@connection.connection_handler
def add_question_to_db(cursor, data):
    cursor.execute("""
                    INSERT INTO question
                    (id, submission_time, view_number, vote_number, title, message, image)
                    VALUES(%(id)s, %(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s);    
                    """,data)



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


@connection.connection_handler
def increment_view_number(cursor, item_id):
    '''
    question = get_question_by_id(item_id)
    question[0]['view_number'] = str(int(question[0]['view_number'])+1)
    questions = edit_question(question, item_id)
    connection.write_data_to_file(connection.QUESTION_FILE, connection.QUESTION_HEADER, questions)
    '''
    cursor.execute('''
                    UPDATE question
                    SET view_number = (SELECT view_number
                                        FROM question
                                        WHERE id = %(question_id)s) + 1
                    WHERE id = %(question_id)s
                    ''',
                   {'question_id': item_id})


def add_line_breaks_to_data(user_data):
    for data in user_data:
        for header, info in data.items():
            if type(info) == str:
                data[header] = info.replace('\n', '<br>')

    return user_data


@connection.connection_handler
def get_question_by_id(cursor, question_id):
    '''
    searched_question = {}
    questions = connection.get_info_from_file(connection.QUESTION_FILE)
    for question in questions:
        if question['id'] == str(question_id):
            for item, value in question.items():
                searched_question[item] = value
    '''
    cursor.execute('''
                    SELECT *
                    FROM question
                    WHERE id = %(question_id)s;
                    ''',
                   {'question_id': question_id})
    searched_question = cursor.fetchall()
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
    try:
        new_id = max((int(data['id']) for data in get_data_from_db(file_name))) + 1
    except ValueError:
        new_id = 0

    return new_id


def add_question(question, image_name):

    if image_name == '':
        image_path = ''

    else:
        image_path = f'{connection.UPLOAD_FOLDER}/{image_name}'

    new_question = {'id':get_new_id('question'),
                  'submission_time':datetime.now(),
                  'view_number':0,
                  'vote_number': 0,
                  'image': image_path}

    for header, data in question.items():
        new_question[header] = data

    return new_question


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
        file.save(os.path.join(connection.UPLOAD_FOLDER, filename))


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


@connection.connection_handler
def get_question_id_by_answer_id(cursor, answer_id):
    cursor.execute("""
        SELECT question_id FROM answer
        WHERE id= %(answer_id)s;
    """, {'answer_id':answer_id})
    question_id = cursor.fetchall()
    if question_id:
        return question_id[0]['question_id']


def delete_question(question_id):
    delete_from_table('answer', 'question_id', question_id)
    delete_from_table('comment', 'question_id', question_id)
    tag_id = get_tag_id(question_id)
    if tag_id:
        delete_from_table('tag', 'id', tag_id)
    delete_from_table('question_tag', 'question_id', question_id)
    delete_from_table('question', 'id', question_id)


@connection.connection_handler
def delete_from_table(cursor, table, parameter, value):
    cursor.execute(sql.SQL("delete from {0} where {1} = %s")
                   .format(sql.Identifier(table),
                           sql.Identifier(parameter)), value)


@connection.connection_handler
def get_tag_id(cursor, question_id):
    cursor.execute("""
        SELECT tag_id from question_tag WHERE question_id=%(question_id)s
    """, {'question_id':question_id})
    tag_id = cursor.fetchall()
    if tag_id:
        return tag_id[0]['tag_id']

