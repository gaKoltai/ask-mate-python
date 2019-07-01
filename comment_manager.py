import connection
from datetime import datetime


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


@connection.connection_handler
def get_ids_by_comment_id(cursor, comment_id):
    cursor.execute('''
                    SELECT question_id, answer_id FROM comment 
                    WHERE id= %(comment_id)s;
                    ''',
                   {'comment_id': comment_id})
    ids = cursor.fetchall()
    return ids[0]


@connection.connection_handler
def update_comment_by_comment_id(cursor, comment_id, message):
    if is_edited_count_none(comment_id=comment_id):
        normalize_edited_count(comment_id=comment_id)
    dt = datetime.now()
    cursor.execute('''
                    UPDATE comment
                    SET message= %(message)s, submission_time = %(dt)s, edited_count=(
                    SELECT edited_count FROM comment WHERE id = %(c_id)s) + 1
                    WHERE id = %(c_id)s;
                    ''',
                   {'message': message,
                    'c_id': comment_id,
                    'dt': dt})


@connection.connection_handler
def get_comment_by_comment_id(cursor, comment_id):
    cursor.execute('''
                    SELECT *
                    FROM comment
                    WHERE id = %(c_id)s;
                    ''',
                   {'c_id': comment_id})
    comment = cursor.fetchall()
    return comment[0]


@connection.connection_handler
def is_edited_count_none(cursor, comment_id):
    cursor.execute('''
                    SELECT edited_count
                    FROM comment
                    WHERE id = %(c_id)s;
                    ''',
                   {'c_id': comment_id})
    e_count = cursor.fetchall()
    if e_count[0]['edited_count'] is not None:
        return False
    else:
        return True


@connection.connection_handler
def normalize_edited_count(cursor, comment_id):
    cursor.execute('''
                    UPDATE comment
                    SET edited_count = 0
                    WHERE id = %(c_id)s;
                    ''',
                   {'c_id': comment_id})