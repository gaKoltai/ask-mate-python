import time
from werkzeug.utils import secure_filename
import os
import connection
import bcrypt



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



def hash_password(plain_text_password):

    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())

    return hashed_bytes.decode('utf-8')


def verify_password(plain_text_password, hashed_password):

    hashed_bytes_password = hashed_password.encode('utf-8')

    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)


