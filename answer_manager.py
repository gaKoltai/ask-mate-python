import connection
from datetime import datetime
import data_manager


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


@connection.connection_handler
def get_answers_by_question_id(cursor, question_id):
    cursor.execute('''
                    SELECT *
                    FROM answer
                    WHERE question_id = %(question_id)s
                    ORDER BY id
                    ''',
                   {'question_id': question_id})
    searched_answers = cursor.fetchall()
    return searched_answers


@connection.connection_handler
def add_answer(cursor, question_id, answer, image_name, user_name):
    if image_name == '':
        image_path = ''
    else:
        image_path = f'{connection.UPLOAD_FOLDER}/{image_name}'
    dt = datetime.now()
    cursor.execute('''
                    INSERT INTO answer
                    (submission_time, vote_number, question_id, message, image, user_id)
                    VALUES (%(time)s, %(vote_num)s, %(question_id)s, %(message)s, %(image)s, (
                    SELECT id FROM users WHERE username = %(username)s));
                    ''',
                   {'time': dt,
                    'vote_num': 0,
                    'question_id': question_id,
                    'message': answer,
                    'image': image_path,
                    'username': user_name}
                   )


def delete_answer_by_answer_id(answer_id):
    data_manager.delete_from_table('comment', 'answer_id', answer_id)
    data_manager.delete_from_table('answer', 'id', answer_id)


def get_answer_ids_by_answers(answers):
    return [answer['id'] for answer in answers]


@connection.connection_handler
def get_answer_by_id(cursor, answer_id):
    cursor.execute('''
                    SELECT * FROM answer
                    WHERE id = %(a_id)s
                    ORDER BY id;
                    ''',
                   {'a_id': answer_id})
    answer = cursor.fetchall()
    return answer[0]


@connection.connection_handler
def edit_answer(cursor, answer_id, answer):

    edited_answer = {key:val for key, val in answer.items()}
    edited_answer['id'] = answer_id

    cursor.execute("""
                    UPDATE answer
                    SET message = %(answer)s
                    WHERE id = %(id)s; 
                    """,edited_answer)