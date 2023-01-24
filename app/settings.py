import os

SECRET_KEY = os.urandom(32)
MAX_CONTENT_LENGTH = 1 * 1024 * 1024
UPLOAD_FOLDER = '/opt/uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv'}

max_lines = 1
trunk_name = 'PJSIP_GW'

MYSQL_IP = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'mysql_user'
MYSQL_PASS = 'mysql_pass'
MYSQL_DB = 'autocalls'

AMI_SRV = 'asterisk.example.lan'
AMI_USER = 'ami_user'
AMI_PASS = 'ami_pass'

