from os import environ


class Config:
    NSLITE_UNITS = environ.get('NSLITE_UNITS', 'mg/ml')
    API_SECRET = environ.get('API_SECRET')
    SECRET_KEY = environ.get('SECRET_KEY')


class ProdConfig(Config):
    NSLITE_TARGET = environ.get('NSLITE_TARGET')
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False


class DevConfig(Config):
    NSLITE_TARGET='127.0.0.1:1337'
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
