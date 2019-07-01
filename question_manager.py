import connection
from datetime import datetime

from answer_manager import get_answers_by_question_id, get_answer_ids_by_answers, delete_answer_by_answer_id
from data_manager import delete_from_table


def search_highlights(searched_phrase, questions):
    for question in questions:
        question['title'] = question['title'].replace(searched_phrase, "<b>" + searched_phrase + "</b>")
        question['message'] = question['message'].replace(searched_phrase, "<b>" + searched_phrase + "</b>")


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
def get_question_by_id(cursor,question_id):
    cursor.execute("""
                    SELECT * FROM question
                    WHERE id = %(question_id)s
                    ORDER BY id;
    """,{'question_id':question_id})

    question = cursor.fetchall()
    return question[0]


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
def get_question_id_by_answer_id(cursor, answer_id):
    cursor.execute("""
        SELECT question_id FROM answer
        WHERE id= %(answer_id)s
        ORDER BY id;
    """, {'answer_id':answer_id})
    question_id = cursor.fetchall()
    if question_id:
        return question_id[0]['question_id']


def delete_question(question_id):
    answers = get_answers_by_question_id(question_id=question_id)
    answer_ids = get_answer_ids_by_answers(answers=answers)
    for answer_id in answer_ids:
        delete_answer_by_answer_id(answer_id)
    delete_from_table('comment', 'question_id', question_id)
    delete_from_table('question_tag', 'question_id', question_id)
    delete_from_table('question', 'id', question_id)


@connection.connection_handler
def search_for_question_ids(cursor, search_phrase):
    cursor.execute("""
                    SELECT id  FROM question
                    WHERE message ILIKE concat('%%', %(search)s, '%%')
                    OR title ILIKE concat('%%', %(search)s, '%%');            
                """,{'search':search_phrase})

    question_ids = cursor.fetchall()

    cursor.execute("""
                    SELECT question_id AS id FROM answer
                    WHERE message ILIKE concat('%%', %(search)s, '%%')
                    """, {'search':search_phrase})

    question_ids_from_answers = cursor.fetchall()

    question_ids = set([item['id'] for item in question_ids])
    question_ids_from_answers = set([item['id'] for item in question_ids_from_answers])

    return list(question_ids | question_ids_from_answers)


@connection.connection_handler
def get_questions_by_id(cursor, question_ids):

    print(question_ids)

    cursor.execute("""
                    SELECT DISTINCT * FROM question
                    WHERE id = ANY (%(question_ids)s)
                    ORDER BY submission_time DESC;
                    """, {'question_ids':question_ids})

    searched_questions=cursor.fetchall()

    return searched_questions


@connection.connection_handler
def get_latest_questions(cursor):
    cursor.execute("""
                    SELECT * FROM question
                    ORDER BY submission_time DESC 
                    LIMIT 5;    
    """,)

    latest_questions = cursor.fetchall()

    return latest_questions