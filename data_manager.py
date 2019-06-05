import connection
from time import asctime, gmtime
import util


def get_post_time(user_data):
    for data in user_data:
        for header, info in data.items():
            if header == 'submission_time':
                data[header] = asctime(gmtime(int(info)))

    return user_data


def sort_data(data, order_by, order_direction):
    is_reversed = False if order_direction == "asc" else True
    order_by = order_by if order_by else 'submission_time'
    if order_by == 'id' or order_by == 'view_number' or order_by == 'vote_number' or order_by == 'submission_time':
        return sorted(data, key=lambda item: int(item[order_by]), reverse=is_reversed)
    else:
        return sorted(data, key=lambda item: item[order_by], reverse=is_reversed)


def vote(item_id, up_or_down, q_or_a):
    if q_or_a == "question":
        f = connection.QUESTION_FILE
        header = connection.QUESTION_HEADER
    else:
        f = connection.ANSWER_FILE
        header = connection.ANSWER_HEADER

    items = connection.get_info_from_file(f)
    print(items)
    for item in items:
        if item_id == int(item['id']):
            item['vote_number'] = int(item['vote_number'])
            item['vote_number'] += 1 if up_or_down == "vote-up" else -1
            item['vote_number'] = str(item['vote_number'])
    connection.write_data_to_file(f, header, items)


def add_line_breaks_to_data(user_data):

    for data in user_data:
        for header, info in data.items():
            if type(info) == str:
                data[header] = info.replace('\n', '<br>')

    return user_data


def get_question_by_id(question_id):
    searched_question = {}
    questions = connection.get_info_from_file(connection.QUESTION_FILE)
    get_post_time(questions)
    for question in questions:
        if question['id'] == str(question_id):
            for item, value in question.items():
                searched_question[item] = value
    return searched_question


def get_answers_by_question_id(question_id):
    searched_answers = []
    answers = connection.get_info_from_file(connection.ANSWER_FILE)
    get_post_time(answers)
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

def edit_question(edited_info, edited_question):
    questions = connection.get_info_from_file(connection.QUESTION_FILE)
    for question in questions:
        if question['id'] == edited_question['id']:
            for header, info in edited_info.items():
                question[header] = edited_info[header]

    return questions



def add_answer(question_id, answer):
    answers = connection.get_info_from_file(connection.ANSWER_FILE)
    new_answer = {'id': str(int(answers[-1]['id']) + 1),
                  'submission_time': util.get_local_time(),
                  'vote_number': 0,
                  'question_id': question_id,
                  'message': answer,
                  "image": 'No image'}
    answers.append(new_answer)
    connection.write_data_to_file(connection.ANSWER_FILE,connection.ANSWER_HEADER, answers)


def delete_answer_by_answer_id(answer_id):
    answers = connection.get_info_from_file(connection.ANSWER_FILE)
    del_answer = None
    for answer in answers:
        if answer['id'] == str(answer_id):
            answers.remove(answer)
    connection.write_data_to_file(connection.ANSWER_FILE, connection.ANSWER_HEADER, answers)


def get_question_id_by_answer_id(answer_id):
    answers = connection.get_info_from_file(connection.ANSWER_FILE)
    question_id = None
    for answer in answers:
        if answer['id'] == str(answer_id):
            question_id = int(answer['question_id'])
    return question_id