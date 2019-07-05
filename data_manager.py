import connection
from psycopg2 import sql
import util
from datetime import datetime


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


@connection.connection_handler
def check_if_user_exists(cursor, user_name, user_email):
    cursor.execute("""
                    SELECT username, email FROM users
                    WHERE username = %(user_name)s OR email = %(user_email)s;
                    """, {'user_name':user_name, 'user_email':user_email})

    user_already_exists = cursor.fetchall()

    if not user_already_exists:
        return False

    return True


@connection.connection_handler
def add_new_user_to_db(cursor, new_user_data):
    cursor.execute("""
                    INSERT INTO users
                    (username, password, email, registration_date) 
                    VALUES (%(username)s, %(password)s, %(email)s, %(registration_date)s)
                    """, new_user_data)


def add_new_user(new_user_data):
    new_user = {}

    for key, val in new_user_data.items():
        new_user[key] = val

    new_user['password'] = util.hash_password(new_user['password'])

    new_user['registration_date'] = datetime.now()

    add_new_user_to_db(new_user)


@connection.connection_handler
def get_user_hash_by_username(cursor, username):
    cursor.execute("""
                    SELECT password FROM users
                    WHERE username = %(username)s
                    """, {'username':username})

    user_hash = cursor.fetchall()

    return user_hash


def check_user_info_for_login(login_data):

    user_hash = get_user_hash_by_username(login_data['username'])
    if not user_hash:
        return False
    if not util.verify_password(login_data['password'], user_hash[0]['password']):
        return False
    return True


@connection.connection_handler
def get_all_user(cursor):
    cursor.execute('''
                    SELECT id,
                     username,
                     email,
                     registration_date
                     FROM users
                    ''')
    users = cursor.fetchall()
    return users


@connection.connection_handler
def get_all_posts_by_user(cursor, table, user_name):

    user_id = get_user_id_by_user_name(user_name)

    cursor.execute(sql.SQL('SELECT id FROM {table} '
                           'WHERE user_id = %(id)s').format(table=sql.Identifier(table)),
                   user_id[0])

    post_ids = cursor.fetchall()

    return post_ids


def verify_if_post_id_matches_users_posts(id_, table, user_name):

    users_posts = get_all_posts_by_user(table, user_name)

    for ids in users_posts:
        if id_ == str(ids['id']):
            print(ids['id'])
            return True

    return False


@connection.connection_handler
def get_user_id_by_user_name(cursor,user_name):
    cursor.execute("""
                    SELECT id from users
                    WHERE username = %(username)s
                    """, {'username': user_name})
    return cursor.fetchall()


@connection.connection_handler
def get_questions_by_user_id(cursor, user_id):
    cursor.execute('''
                    SELECT id, title, message
                    FROM question
                    WHERE user_id = %(user_id)s;
                    ''',
                   {'user_id': user_id})
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def get_answers_by_user_id(cursor, user_id):
    cursor.execute('''
                    SELECT q.id AS question_id,
                     q.title AS question_title,
                     a.id AS answer_id,
                     a.message AS answer_message
                    FROM answer a
                    INNER JOIN question q
                        ON a.question_id = q.id
                    where a.user_id = %(user_id)s
                    ''',
                   {'user_id': user_id})
    answers = cursor.fetchall()
    return answers


@connection.connection_handler
def get_question_comments_by_user_id(cursor, user_id):
    cursor.execute('''
                    SELECT c.id AS comment_id,
                           c.message AS comment_message,
                           q.id AS question_id,
                           q.title AS question_title
                    FROM comment c
                    INNER JOIN question q
                        ON c.question_id = q.id
                    WHERE c.user_id = %(user_id)s;
                    ''', {'user_id': user_id})
    question_comments = cursor.fetchall()
    return question_comments


@connection.connection_handler
def get_answer_comments_by_user_id(cursor, user_id):
    cursor.execute('''
                    SELECT c.id AS comment_id,
                           c.message AS comment_message,
                           a.id AS answer_id,
                           a.message AS answer_message,
                           q.id AS question_id,
                           q.title AS question_title
                    FROM comment c
                    INNER JOIN answer a
                        ON c.answer_id = a.id
                    INNER JOIN question q
                        ON a.question_id = q.id
                    WHERE c.user_id = %(user_id)s;
                    ''', {'user_id': user_id})
    answer_comments = cursor.fetchall()
    return answer_comments


@connection.connection_handler
def get_user_by_user_id(cursor, user_id):
    cursor.execute('''
                    SELECT id, username, email
                    FROM users
                    WHERE id = %(user_id)s;
                    ''', {'user_id': user_id})
    user_data = cursor.fetchall()
    return user_data[0]