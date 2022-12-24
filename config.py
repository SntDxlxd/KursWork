import os

DB_NAME = 'onread'
DB_USER = 'admin'
USER_PASSWORD = 'admin'
DB_HOST = '5432'
DB_PORT = 'localhost'


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ya-vizhivu'