import datetime
from flask import *   
import logging
import os
from flask_compress import Compress
from flask_talisman import Talisman
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flaskblog.config import Config, CACHE_CONFIG, CSP, format_love
from flask_marshmallow import Marshmallow
from flask_caching import Cache
import redis
import flask_monitoringdashboard as dashboard
from flaskblog.celery_config import celery_init_app
import websockets

from py2neo import Graph
from py2neo.errors import ServiceUnavailable

import json

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

# neo4j
graph = Graph('neo4j+ssc://ec62436d.databases.neo4j.io:7687',
 auth=('neo4j', 'VDfDjirn7pFB64intj1yPLzdZowzg2HLeI-NdeHqhO4'))
try:
    graph.run("RETURN 1")
    print(True)
except ServiceUnavailable:
    print(False)


app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy()
ma = Marshmallow()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message = None
login_manager.session_protection = "strong"
REMEMBER_COOKIE_NAME= 'remember_token'
REMEMBER_COOKIE_DURATION=datetime.timedelta(days=64, seconds=29156, microseconds=10)
REMEMBER_COOKIE_REFRESH_EACH_REQUEST=False
io = SocketIO(app, async_mode='threading', transport=websockets)
#io = SocketIO()
mail = Mail()
jwt = JWTManager()
compress = Compress()
cache = Cache(config=CACHE_CONFIG)
talisman = Talisman(content_security_policy=CSP)

def create_app(config_class=Config):
    db.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    io.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    #dashboard.bind(app)
    compress.init_app(app)
    talisman.init_app(app) 
    celery=celery_init_app(app)
    celery.conf.update(
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        timezone='UTC',
        enable_utc=True,
    )
    app.jinja_env.filters['format_love'] = format_love


    
    from flaskblog.users.routes import users
    from flaskblog.groups.routes import groups
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    from flaskblog.main.dummy.dummy import dummy
    from flaskblog.main.api.api import api

    from flaskblog.rooms.socket_routes import sock
    from flaskblog.business.routes import business
    from flaskblog.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(groups)
    app.register_blueprint(posts)
    app.register_blueprint(sock)
    app.register_blueprint(main)
    app.register_blueprint(dummy)
    app.register_blueprint(business)
    app.register_blueprint(errors)
    
    return app, celery
