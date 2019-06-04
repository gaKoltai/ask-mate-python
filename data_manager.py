import connection
from time import asctime, gmtime
import util


def get_post_time(user_data):
    for data in user_data:
        for header, info in data.items():
            if header == 'submission_time':
                data[header] = asctime(gmtime(int(info)))

    return user_data


def vote(id, up_or_down):
    questions = connection.get_info_from_file(connection.QUESTION_FILE)
    for question in questions:
        if id == int(question['id']):
            question['vote_number'] = int(question['vote_number'])
            question['vote_number'] += 1 if up_or_down == "vote-up" else -1
            question['vote_number'] = str(question['vote_number'])
    connection.write_data_to_file(connection.QUESTION_FILE, connection.QUESTION_HEADER, questions)


def add_line_breaks_to_data(user_data):

    for data in user_data:
        for header, info in data.items():
            if type(info) == str:
                data[header] = info.replace('\n', '<br>')

    return user_data


def get_question_by_id(question_id):
    searched_question = {}
    questions = connection.get_info_from_file(connection.QUESTION_FILE)
    for question in questions:
        if question['id'] == str(question_id):
            for item, value in question.items():
                searched_question[item] = value
    return searched_question


def get_answers_by_question_id(question_id):
    searched_answers = []
    answers = connection.get_info_from_file(connection.ANSWER_FILE)
    for answer in answers:
        if answer['question_id'] == str(question_id):
            searched_answers.append(answer)
    return searched_answers


def get_new_id(file_name):
    new_id = len(connection.get_info_from_file(file_name))

    return new_id

def new_question_entry(entry_data):
    id = get_new_id(connection.QUESTION_FILE)
    post_time = util.get_local_time()

    new_entry = {'id':id, 'submission_time':post_time, 'view_number':0, 'vote_number': 0 }

    for header, data in entry_data.items():
        new_entry[header] = data

    return new_entry
