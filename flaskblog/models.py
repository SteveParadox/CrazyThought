from datetime import datetime

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskblog import db, login_manager, app, ma
from flask_login import UserMixin
from marshmallow_sqlalchemy import ModelSchema


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __searchable__=['username']

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    posts = db.relationship('Post', backref='author', lazy=True)
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
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now(tz=None))
    content = db.Column(db.Text, nullable=False)
    comments = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    img_filename = db.Column(db.String())
    img_data = db.Column(db.LargeBinary)
    comment = db.relationship('Comment', backref='parser', lazy=True)

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

    def __repr__(self):
        return '<Comment %r>' % self.name


'''class Translate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
'''
class UserSchema(ModelSchema):
    class Meta:
        fields= ('id', 'username', 'email', 'image_file', 'password', 'posts', 'comments' )

        model = User
user_schema= UserSchema()
users_schema=  UserSchema(many=True)



class PostSchema(ModelSchema):
    class Meta:
        model = Post
post_schema= PostSchema()
posts_schema=  PostSchema(many=True)


class CommentSchema(ModelSchema):
    class Meta:
        model = Comment
comment_schema= CommentSchema()
comments_schema=  CommentSchema(many=True)

