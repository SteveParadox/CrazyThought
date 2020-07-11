import datetime
from flask import *
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flaskblog.config import Config


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
socketio = SocketIO()
mail = Mail()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)
    jwt.init_app(app)

    from flaskblog.users.routes import users
    from flaskblog.groups.routes import groups
    from flaskblog.api.routes import api
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    from flaskblog.business.routes import business
    from flaskblog.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(groups)
    app.register_blueprint(api)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(business)
    app.register_blueprint(errors)

    return app
