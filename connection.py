import csv

ANSWER_HEADER = ["id","submission_time","vote_number","question_id","message","image"]
QUESTION_HEADER = ["id","submission_time","view_number","vote_number","title","message","image"]
ANSWER_FILE = "/sample_data/answer.csv"
QUESTION_FILE = "/sample_data/quest"


def get_info_from_file(file):
    with open(file) as csv_file:
        user_data = [data for data in csv.DictReader(file)]

    return user_data


