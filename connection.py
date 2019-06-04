import csv

ANSWER_HEADER = ["id","submission_time","vote_number","question_id","message","image"]
QUESTION_HEADER = ["id","submission_time","view_number","vote_number","title","message","image"]
ANSWER_FILE = "sample_data/answer.csv"
QUESTION_FILE = "sample_data/question.csv"


def get_info_from_file(file_name):
    with open(file_name) as csv_file:
        user_data = [data for data in csv.DictReader(csv_file)]

    return user_data


def write_data_to_file(file_name, header, data):
    with open(file_name, "w", newline='') as csv_file:
        writer = csv.DictWriter(csv_file, header)
        writer.writeheader()
        for item in data:
            writer.writerow(item)


def pass_user_story_to_file(user_data, file_name):

    with open(file_name, 'a', newline='') as csv_file:
        writer = csv.DictWriter(csv_file)
        writer.writerow(user_data)
