import connection
import time


def get_post_time(user_data):
    for data in user_data:
        for header, info in data.items():
            if header == 'submission_time':
                data[header] = time.asctime(time.gmtime(int(info)))

    return user_data


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