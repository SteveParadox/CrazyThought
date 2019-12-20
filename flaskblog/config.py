import os

basedir = os.path.abspath(os.path.dirname(__file__))
TOP_LEVEL_DIR = os.path.abspath(os.curdir)
WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50


class Config:
    ENV = 'dev'

    if ENV == 'dev':
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    else:

        SQLALCHEMY_DATABASE_URI = 'postgres://bzzbbjdumbntco:4ee5a8c0e94e274c2c1979b20ac2e93c4395204909169803627e12d7577fbdae@ec2-174-129-255-37.compute-1.amazonaws.com:5432/dcjhrsk5ihpbfr'

    SECRET_KEY=os.environ.get('SECRET_KEY')

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    SQLALCHEMY_TRACK_MODIFICATIONS= True




