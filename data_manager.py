import connection
from datetime import datetime
import util
import os
from werkzeug.utils import secure_filename
from psycopg2 import sql


@connection.connection_handler
def get_data_from_db(cursor, table, order_by= None, order_direction=None):
    order_by = 'submission_time' if not order_by else order_by
    if order_direction == "desc":
        cursor.execute(
            sql.SQL("SELECT * FROM {table} ORDER BY {order_by} DESC").
                format(table=sql.Identifier(table),
                       order_by=sql.Identifier(order_by)))
    else:
        cursor.execute(
            sql.SQL("SELECT * FROM {table} ORDER BY {order_by}").
                format(table=sql.Identifier(table), order_by=sql.Identifier(order_by)))
    data = cursor.fetchall()
    return data


@connection.connection_handler
def add_question_to_db(cursor, data):
    cursor.execute("""
                    INSERT INTO question
                    (submission_time, view_number, vote_number, title, message, image)
                    VALUES(%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s);    
                    """,data)


@connection.connection_handler
def vote_question(cursor, vote, id):
    cursor.execute("""
        UPDATE question
        SET vote_number = vote_number + %(vote)s
        WHERE id=%(id)s;
        """, {'id': id, 'vote': vote})


@connection.connection_handler
def vote_answer(cursor, vote, id):
    cursor.execute("""
        UPDATE answer
        SET vote_number = vote_number + %(vote)s
        WHERE id=%(id)s;
        """, {'id': id, 'vote': vote})


@connection.connection_handler
def increment_view_number(cursor, item_id):
    cursor.execute('''
                    UPDATE question
                    SET view_number = (SELECT view_number
                                        FROM question
                                        WHERE id = %(question_id)s) + 1
                    WHERE id = %(question_id)s;
                    ''',
                   {'question_id': item_id})


def add_line_breaks_to_data(user_data):
    for data in user_data:
        for header, info in data.items():
            if type(info) == str:
                data[header] = info.replace('\n', '<br>')

    return user_data


@connection.connection_handler
def get_question_by_id(cursor,question_id):
    cursor.execute("""
                    SELECT * FROM question
                    WHERE id = %(question_id)s;
    """,{'question_id':question_id})

    question = cursor.fetchall()
    return question[0]


@connection.connection_handler
def get_answers_by_question_id(cursor, question_id):
    cursor.execute('''
                    SELECT *
                    FROM answer
                    WHERE question_id = %(question_id)s
                    ''',
                   {'question_id': question_id})
    searched_answers = cursor.fetchall()
    return searched_answers


def add_question(question, image_name):

    new_question = {}

    if image_name == '':
        image_path = ''
    else:
        image_path = f'{connection.UPLOAD_FOLDER}/{image_name}'

    for header,data in question.items():
        new_question[header] = data

    new_question_default = {'submission_time':datetime.now(),
                  'view_number': 0,
                  'vote_number': 0,
                  'image': image_path}
    for header, data in new_question_default.items():
        new_question[header] = data

    return new_question


@connection.connection_handler
def edit_question(cursor, data_to_edit, question_id):

    edited_data = {key:val for key, val in data_to_edit.items()}
    edited_data['question_id'] = question_id

    cursor.execute("""
                    UPDATE question
                    SET (title, message) = (%(title)s, %(message)s)
                    WHERE id = %(question_id)s;
    """,edited_data)


@connection.connection_handler
def add_answer(cursor, question_id, answer, image_name):
    if image_name == '':
        image_path = ''
    else:
        image_path = f'{connection.UPLOAD_FOLDER}/{image_name}'
    dt = datetime.now()
    cursor.execute('''
                    INSERT INTO answer
                    (submission_time, vote_number, question_id, message, image)
                    VALUES (%(time)s, %(vote_num)s, %(question_id)s, %(message)s, %(image)s);
                    ''',
                   {'time': dt,
                    'vote_num': 0,
                    'question_id': question_id,
                    'message': answer,
                    'image': image_path}
                   )


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in connection.ALLOWED_FILE_EXTENSIONS


def upload_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(connection.UPLOAD_FOLDER, filename))


def delete_answer_by_answer_id(answer_id):
    delete_from_table('comment', 'answer_id', answer_id)
    delete_from_table('answer', 'id', answer_id)


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
    cursor.execute(sql.SQL("DELETE FROM {0} WHERE {1} = %s")
                   .format(sql.Identifier(table),
                           sql.Identifier(parameter)), value)


@connection.connection_handler
def get_tag_id(cursor, question_id):
    cursor.execute("""
        SELECT tag_id FROM question_tag WHERE question_id=%(question_id)s
    """, {'question_id':question_id})
    tag_id = cursor.fetchall()
    if tag_id:
        return tag_id[0]['tag_id']


@connection.connection_handler
def add_comment_to_question(cursor, comment_message, question_id):
    dt = datetime.now()
    cursor.execute('''
                    INSERT INTO comment
                    (question_id, answer_id, message, submission_time)
                     VALUES (%(question_id)s,
                                NULL,
                                %(message)s,
                                %(time)s);
                    ''', {'question_id': question_id,
                          'message': comment_message,
                          'time': dt})


@connection.connection_handler
def get_comment_by_question_id(cursor, question_id):
    cursor.execute('''
                    SELECT id, message, submission_time, edited_count FROM comment
                    WHERE question_id = %(q_id)s;
                    ''',
                   {'q_id': question_id})
    comment = cursor.fetchall()
    return comment


@connection.connection_handler
def add_comment_to_answer(cursor, comment_message, answer_id):
    dt = datetime.now()
    cursor.execute('''
                    INSERT INTO comment
                    (question_id, answer_id, message, submission_time)
                     VALUES (   NULL,
                                %(answer_id)s,
                                %(message)s,
                                %(time)s);
                    ''', {'answer_id': answer_id,
                          'message': comment_message,
                          'time': dt})


@connection.connection_handler
def get_comments_by_answer_id(cursor, answer_ids):
    cursor.execute('''
                    SELECT * FROM comment
                    WHERE answer_id IN %(a_id)s;
                    ''',
                   {'a_id': answer_ids})
    comments = cursor.fetchall()
    return comments


def get_answer_ids_by_answers(answers):
    return [answer['id'] for answer in answers]


@connection.connection_handler
def get_answer_by_id(cursor, answer_id):
    cursor.execute('''
                    SELECT * FROM answer
                    WHERE id = %(a_id)s;
                    ''',
                   {'a_id': answer_id})
    answer = cursor.fetchall()
    return answer[0]