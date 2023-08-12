import os
from google_auth_oauthlib.flow import Flow


CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://default:RIb4Sy6hNvnuRxSR8us3S99paPOCAU21@redis-12331.c309.us-east-2-1.ec2.cloud.redislabs.com:12331',
    'CACHE_DEFAULT_TIMEOUT': 3000,  
    'CACHE_REDIS_SOCKET_TIMEOUT': 30,
}

CELERY_CONFIG = {
        "broker_url":CACHE_CONFIG['CACHE_REDIS_URL'],
        "result_backend":CACHE_CONFIG['CACHE_REDIS_URL']
    }

CSP = {
    'default-src': ["'self'"],
    'script-src': ["'self'"],
    'style-src': ["'self'"],
    'img-src': ["'self'", 'data:'],
}

CLIENT_SECRET="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"
CLIENT_ID = "686365316167-9r4fermoon4l0c3q1n4vj8o5mh1l6mi0.apps.googleusercontent.com"

abs_client_secrets_path = os.path.abspath(r"C:\Users\USER\Desktop\CrazyThought\flaskblog\client_secrets.json")
flow = Flow.from_client_secrets_file(
    abs_client_secrets_path,  
    scopes=["openid", "email", "profile"],
    redirect_uri='http://localhost:5000/google/callback'  
)

class Config:
    SECRET_KEY = '795849f0d2328258710ae9c71cb4b5ea'
    ENV = 'dev'

    if ENV == 'dev':
        SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    else:
        SQLALCHEMY_DATABASE_URI = 'postgresql://crazythought:QZrbDltSwmk0FgOlPTFl@crazythoughtdb.cikwkjt4xyvu.us-east-1.rds.amazonaws.com:5432/crazythoughtdb'

    SECURITY_PASSWORD_SALT = 'my_precious_two'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'crazythoughtverify@gmail.com'
    MAIL_PASSWORD = 'DRstrange11..'
    MAIL_DEFAULT_SENDER = 'from@example.com'
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_POOL_TIMEOUT = 3000
    SQLALCHEMY_POOL_RECYCLE = 3600 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
 
    #CACHE_TYPE = 'simple'


def format_love(value):
    if value >= 1000000:
        return f"{value / 1000000:.1f}M"
    elif value >= 1000:
        return f"{value / 1000:.1f}K"
    else:
        return str(value)





