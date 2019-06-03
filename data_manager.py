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

