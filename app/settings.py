import os

SECRET_KEY = os.urandom(32)
MAX_CONTENT_LENGTH = 1 * 1024 * 1024
UPLOAD_FOLDER = '/opt/uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv'}

max_lines = 1
trunk_name = '1111'

MYSQL_CONN = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'mysql_user',
    'password': 'mysql_pass',
    'database': 'autocalls'
}

AMI_CONN = {
    'address': '127.0.0.1',
    'port': 5038,
    'timeout': 60
}
AMI_CREDS = {
    'username': 'ami_user',
    'secret': 'ami_pass'
}

