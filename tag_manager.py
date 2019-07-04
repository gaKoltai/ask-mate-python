import connection
from psycopg2 import sql


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
    """, {'question_id': question_id,
          'tag_id': tag_id})


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


@connection.connection_handler
def get_tags_with_number(cursor):
    cursor.execute(
        """
        SELECT  tag.id, tag.name, COUNT(question_tag.tag_id) as count FROM tag
        RIGHT JOIN question_tag on(question_tag.tag_id = tag.id)
        GROUP BY tag.name,tag.id;
        """)
    return cursor.fetchall()


@connection.connection_handler
def get_questions_by_tag_id(cursor, tag_id, order_by, order_direction):
    order_by = 'submission_time' if not order_by else order_by
    if order_direction == "desc":
        cursor.execute(
            sql.SQL("SELECT question.* FROM question LEFT JOIN question_tag qt on question.id = qt.question_id WHERE qt.tag_id = %(tag_id)s ORDER BY {order_by} DESC").
                format(order_by=sql.Identifier(order_by)), {'tag_id': tag_id})
    else:
        cursor.execute(
            sql.SQL(
                "SELECT question.* FROM question LEFT JOIN question_tag qt on question.id = qt.question_id WHERE qt.tag_id = %(tag_id)s ORDER BY {order_by}").
                format(order_by=sql.Identifier(order_by)), {'tag_id': tag_id})
    return cursor.fetchall()