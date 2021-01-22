import os
#import json


basedir = os.path.abspath(os.path.dirname(__file__))
TOP_LEVEL_DIR = os.path.abspath(os.curdir)
WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50

'''with open('/etc/config.json') as config_file:
    config = json.load(config_file)
'''
class Config:
    SECRET_KEY = '795849f0d2328258710ae9c71cb4b5ea'
    ENV = 'prod'

    if ENV == 'dev':
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    else:

        SQLALCHEMY_DATABASE_URI = 'postgres://xtxivwdedrdqiq:dca0e349351bad9191732318455e178bd99eec6326c351c09a4d70b475833b32@ec2-174-129-32-240.compute-1.amazonaws.com:5432/dagkfphn1hgj9d'

    SECURITY_PASSWORD_SALT = 'my_precious_two'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'crazythoughtverify@gmail.com'
    MAIL_PASSWORD = 'DRstrange11..'
    MAIL_DEFAULT_SENDER = 'from@example.com'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    BABEL_DEFAULT_LOCALE = 'en'
    WHOOSH_BASE = 'whoosh'





