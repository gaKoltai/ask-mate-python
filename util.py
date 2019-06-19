import time
from werkzeug.utils import secure_filename
import os
import connection


def get_local_time():
    current_time = int(time.time())

    return current_time


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in connection.ALLOWED_FILE_EXTENSIONS


def upload_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(connection.UPLOAD_FOLDER, filename))