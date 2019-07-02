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