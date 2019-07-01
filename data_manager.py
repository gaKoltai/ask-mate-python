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


def add_new_user(new_user_data):
    new_user = {}

    for key, val in new_user_data.items():
        new_user[key] = val

    new_user['password'] = util.hash_password(new_user['password'])

    new_user['registration_date'] = datetime.now()