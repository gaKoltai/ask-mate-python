import connection
from datetime import datetime
from psycopg2 import sql


#GENERAL DATA MANAGER functions

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
def delete_from_table(cursor, table, parameter, value):
    cursor.execute(sql.SQL("DELETE FROM {0} WHERE {1} = %s")
                   .format(sql.Identifier(table),
                           sql.Identifier(parameter)), [value])


#functions dealing with questions

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
                    WHERE id = %(question_id)s;
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
        WHERE id= %(answer_id)s;
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
    tag_id = get_tag_ids(question_id)
    if tag_id:
        for id_ in tag_id:
            delete_from_table('tag', 'id', id_['tag_id'])
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


#functions dealing with answers

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
                    ''',
                   {'question_id': question_id})
    searched_answers = cursor.fetchall()
    return searched_answers


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


def delete_answer_by_answer_id(answer_id):
    delete_from_table('comment', 'answer_id', answer_id)
    delete_from_table('answer', 'id', answer_id)


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


@connection.connection_handler
def edit_answer(cursor, answer_id, answer):

    edited_answer = {key:val for key, val in answer.items()}
    edited_answer['id'] = answer_id

    cursor.execute("""
                    UPDATE answer
                    SET message = %(answer)s
                    WHERE id = %(id)s; 
                    """,edited_answer)


#functions dealing with TAGS


def get_question_tags( question_id):
    tag_ids = get_tag_ids(question_id)
    tags = get_all_tags()
    if tag_ids:
        tags = [tag for tag in tags if tag['id'] in tag_ids]
    else:
        return None
    return tags


def get_rest_of_tags( question_id):
    tag_ids = get_tag_ids(question_id)
    tags = get_all_tags()
    if tag_ids:
        tags = [tag for tag in tags if tag['id'] not in tag_ids]

    return tags


@connection.connection_handler
def get_all_tags(cursor):
    cursor.execute("""
                        SELECT * FROM tag;
                    """)
    return cursor.fetchall()


@connection.connection_handler
def get_tag_ids(cursor, question_id):
    cursor.execute("""
        SELECT tag_id FROM question_tag WHERE question_id=%(question_id)s;
    """, {'question_id': question_id})
    tags = cursor.fetchall()
    if tags:
        tag_ids = tuple(tag['tag_id'] for tag in tags)

        return tag_ids


@connection.connection_handler
def add_tag(cursor, question_id, tag_id):
    cursor.execute("""
        INSERT INTO question_tag(question_id, tag_id)
        VALUES(%(question_id)s, %(tag_id)s);
    """, {'question_id':question_id,
          'tag_id':tag_id})


@connection.connection_handler
def remove_tag(cursor, question_id, tag_id):
    cursor.execute("""
        DELETE FROM question_tag
        WHERE tag_id=%(tag_id)s
        AND question_id= %(question_id)s;
    """, {'question_id':question_id,
          'tag_id':tag_id})


@connection.connection_handler
def new_tag(cursor, tag_name):
    cursor.execute("""
            INSERT INTO tag(name)
            VALUES(%(tag_name)s);
        """, {'tag_name': tag_name})


#functions dealing with COMMENTS

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