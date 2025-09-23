print("Loading config.py")

import os

class Config:
    ALLOWED_USERS = ['bob', 'alice', 'eve']
    ADMIN_USERS = ['alice']
    MAX_FILE_SIZE_MB = 5
    ALLOWED_EXTENSIONS = {'log', 'csv'}
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key-that-should-be-in-an-env-file'
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    BOTO3_BUCKET_NAME = os.environ.get('BOTO3_BUCKET_NAME')