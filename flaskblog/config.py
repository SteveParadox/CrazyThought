import os
from google_auth_oauthlib.flow import Flow
from dotenv import load_dotenv

load_dotenv()

CACHE_CONFIG = {
    'CACHE_TYPE': os.environ.get('CACHE_TYPE'),
    'CACHE_REDIS_URL':  os.environ.get('CACHE_REDIS_URL'),
    'CACHE_DEFAULT_TIMEOUT':  os.environ.get('CACHE_DEFAULT_TIMEOUT'),  
    'CACHE_REDIS_SOCKET_TIMEOUT':  os.environ.get('CACHE_REDIS_SOCKET_TIMEOUT'),
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

CLIENT_SECRET= os.environ.get('CLIENT_SECRET')
CLIENT_ID = os.environ.get('CLIENT_ID')


abs_client_secrets_path = os.path.join(os.getcwd(), "./flaskblog/client_secrets.json")
flow = Flow.from_client_secrets_file(
    abs_client_secrets_path,  
    scopes=["openid", "email", "profile"],
    redirect_uri='http://localhost:5000/google/callback'  
)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ENV = 'dev'

    if ENV == 'dev':
        SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    SECURITY_PASSWORD_SALT =  os.environ.get('SECURITY_PASSWORD_SALT')
    MAIL_SERVER =  os.environ.get('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME =  os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD =  os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = 'from@example.com'
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_POOL_TIMEOUT = 3000
    SQLALCHEMY_POOL_RECYCLE = 3600 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
    SSL_KEY = r'C:\Users\USER\Desktop\CrazyThought\certs\private_key.pem'
    SSL_CERT = r'C:\Users\USER\Desktop\CrazyThought\certs\certificate.pem'


def format_love(value):
    if value >= 1000000:
        return f"{value / 1000000:.1f}M"
    elif value >= 1000:
        return f"{value / 1000:.1f}K"
    else:
        return str(value)





