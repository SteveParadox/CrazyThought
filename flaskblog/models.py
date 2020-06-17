from datetime import datetime

from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from marshmallow_sqlalchemy import ModelSchema

from flaskblog import db, login_manager, app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __searchable__ = ['username']

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    business = db.relationship('Business', backref='therapy', lazy=True)
    patient = db.relationship('Patient', backref='pati', lazy=True)
    admin = db.relationship('Admin', backref='adm', lazy=True)
    comments = db.relationship('Comment', backref='reply', lazy=True)


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}'), '{self.confirmed}')"


class Post(db.Model):
    __searchable__ = ['content']
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text, nullable=False)
    comments = db.Column(db.Integer, default=0)
    # tag = db.Column(db.Integer,  nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    img_filename = db.Column(db.String())
    img_data = db.Column(db.LargeBinary)
    comment = db.relationship('Comment', backref='parser', lazy=True)
    admin = db.relationship('Admin', backref='admini', lazy=True)

    # translate = db.relationship('Translate', backref='translation', lazy=True)

    def __repr__(self):
        return f"Post( '{self.date_posted}'), '{self.content}' "


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    reply_message = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String())
    post = db.relationship('Post', backref=db.backref('post', lazy=True))
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.Boolean, default=False)
    admin = db.relationship('Admin', backref='administration', lazy=True)

    def __repr__(self):
        return '<Comment %r>' % self.name


class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    degree = db.Column(db.String(), nullable=False)
    licence_no = db.Column(db.String(), nullable=False, unique=True)
    aim = db.Column(db.Text())

    year_of_licence = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return '<Business %r>' % self.name


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_post = db.Column(db.Text())

    def __repr__(self):
        return '<Patient %r>' % self.name


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    report_a_problem = db.Column(db.Text)
    report_post = db.Column(db.Text)


    def __repr__(self):
        return '<Admin %r>' % self.name


class UserSchema(ModelSchema):
    class Meta:
        fields = ('id', 'username', 'email', 'image_file', 'password', 'posts', 'comments')

        model = User


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class PostSchema(ModelSchema):
    class Meta:
        model = Post


post_schema = PostSchema()
posts_schema = PostSchema(many=True)


class CommentSchema(ModelSchema):
    class Meta:
        model = Comment


comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
