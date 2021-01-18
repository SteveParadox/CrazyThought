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
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    business = db.relationship('Business', backref='therapy', lazy=True)
    patient = db.relationship('Patient', backref='pati', lazy=True)
    admin = db.relationship('Admin', backref='adm', lazy=True)
    comments = db.relationship('Comment', backref='reply', lazy=True)
    images = db.relationship('Images', backref='imgs', lazy=True)
    videos = db.relationship('Videos', backref='vids', lazy=True)
    media_comments = db.relationship('Media_Comments', backref='reple', lazy=True)
    media_comment = db.relationship('Media_Comment', backref='repli', lazy=True)
    topics = db.relationship('Topic', backref='creator', lazy=True)
    groups = db.relationship('Groups', backref='group', lazy=True)
    group_comment = db.relationship('Group_comment', backref='disc', lazy=True)
    reply_comment = db.relationship('ReplyComment', backref='comment', lazy=True)
    group_reply_comment = db.relationship('GroupReplyComment', backref='g_reply', lazy=True)
    media_reply_comment = db.relationship('MediaReplyComment', backref='vid_reply', lazy=True)
    media_reply_comments = db.relationship('MediaReplyComments', backref='img_reply', lazy=True)

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


class Topic(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    groups = db.relationship('Groups', backref='title', lazy=True)
    pub_id = db.Column(db.String(50), unique=True)
    popular = db.Column(db.Integer, default=0)


class Groups(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    comments = db.Column(db.Integer, default=0)
    group_love = db.Column(db.Integer, default=0)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    # user= db.relationship(User, secondary='link')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.relationship('Group_comment', backref='discuss', lazy=True)


"""class Link(db.Model):
    user_id = db.Column(db.Integer,
                       db.ForeignKey('user.id'),
                       primary_key = True)

    groups_id = db.Column(db.Integer,
                          db.ForeignKey('groups.id'),
                          primary_key = True)"""


class Group_comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    group_upvote = db.Column(db.Integer, default=0)
    reply_message = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String())
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.Boolean, default=False)
    grp_comment = db.relationship('GroupReplyComment', backref='grp_rep', lazy=True)
    groups_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    replys = db.Column(db.Integer, default=0)


class GroupReplyComment(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    upvote = db.Column(db.Integer, default=0)
    group_comment = db.Column(db.Integer, db.ForeignKey('group_comment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String())
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.Boolean, default=False)


class Post(db.Model):
    __searchable__ = ['content']
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text, nullable=False)
    comments = db.Column(db.Integer, default=0)
    love = db.Column(db.Integer, default=0)
    # tag = db.Column(db.Integer,  nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.relationship('Comment', backref='parser', lazy=True)
    rc = db.relationship('ReplyComment', backref='repc', lazy=True)
    admin = db.relationship('Admin', backref='admini', lazy=True)
    viewed = db.Column(db.Integer, default=0)
    extra = db.Column(db.String())

    # translate = db.relationship('Translate', backref='translation', lazy=True)

    def __repr__(self):
        return f"Post( '{self.date_posted}'), '{self.content}' "


class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plic_id = db.Column(db.String(50), unique=True)
    img_love = db.Column(db.Integer, default=0)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    photo_filename = db.Column(db.String())
    photo_data = db.Column(db.LargeBinary)
    comments = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    media_comments = db.relationship('Media_Comments', backref='img', lazy=True)

    def __repr__(self):
        return f"Images( '{self.photo_filename}'), '{self.photo_data}' "


class Videos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    publ_id = db.Column(db.String(50), unique=True)
    video_love = db.Column(db.Integer, default=0)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    img_filename = db.Column(db.String())
    img_data = db.Column(db.LargeBinary)
    comments = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    media_comment = db.relationship('Media_Comment', backref='vid', lazy=True)

    def __repr__(self):
        return f"Videos( '{self.img_filename}'), '{self.img_data}' "


class Comment(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    reply_message = db.Column(db.Text)
    upvote = db.Column(db.Integer, default=0)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String())
    post = db.relationship('Post', backref=db.backref('post', lazy=True))
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.Boolean, default=False)
    replys = db.Column(db.Integer, default=0)
    admin = db.relationship('Admin', backref='administration', lazy=True)
    reply_comment = db.relationship('ReplyComment', backref='comments', lazy=True)

    def __repr__(self):
        return '<Comment %r>' % self.name


class ReplyComment(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    upvote = db.Column(db.Integer, default=0)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String())
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.Boolean, default=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return '<ReplyComment %r>' % self.name


class Media_Comment(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    vid_upvote = db.Column(db.Integer, default=0)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    videos_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.Boolean, default=False)
    name = db.Column(db.String())
    replys = db.Column(db.Integer, default=0)
    media_reply_comment = db.relationship('MediaReplyComment', backref='med_rep', lazy=True)

    def __repr__(self):
        return '<Media_Comment %r>' % self.name


class MediaReplyComment(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    upvote = db.Column(db.Integer, default=0)
    media_comment_id = db.Column(db.Integer, db.ForeignKey('media__comment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String())

    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<MediaReplyComment %r>' % self.name


class Media_Comments(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    img_upvote = db.Column(db.Integer, default=0)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    images_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.Boolean, default=False)
    name = db.Column(db.String())
    replys = db.Column(db.Integer, default=0)
    media_reply_comments = db.relationship('MediaReplyComments', backref='med_reps', lazy=True)

    def __repr__(self):
        return '<Media_Comment %r>' % self.name


class MediaReplyComments(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    upvote = db.Column(db.Integer, default=0)
    media_comments_id = db.Column(db.Integer, db.ForeignKey('media__comments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String())
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<MediaReplyComments %r>' % self.name


class Business(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    degree = db.Column(db.String(), nullable=False)
    licence_no = db.Column(db.String(), nullable=False, unique=True)
    aim = db.Column(db.Text())

    year_of_licence = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return '<Business %r>' % self.name


class Patient(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_post = db.Column(db.Text())

    def __repr__(self):
        return '<Patient %r>' % self.name


class Admin(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    report_a_problem = db.Column(db.Text)
    report_post = db.Column(db.Text)

    def __repr__(self):
        return '<Admin %r>' % self.name


class Client(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscription = db.Column(db.Integer)
    earnings = db.Column(db.Integer)
    total_users = db.Column(db.Integer)


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(), nullable=False)
    unique_id = db.Column(db.String(), unique=True, nullable=False)
    host = db.Column(db.String(), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    msg = db.relationship('Messages', backref='msgs', lazy=True)


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    message = db.Column(db.String())
    date = db.Column(db.String(20))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    # created = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"Messages('{self.username}', '{self.message}')"


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


class MessagesSchema(ModelSchema):
    class Meta:
        model = Messages


messages_schema = MessagesSchema()
messages_schemas = MessagesSchema(many=True)


class CommentSchema(ModelSchema):
    class Meta:
        model = Comment


comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)


class ReplyCommentSchema(ModelSchema):
    class Meta:
        model = ReplyComment


reply_comment_schema = ReplyCommentSchema()
reply_comments_schema = ReplyCommentSchema(many=True)


class AdminSchema(ModelSchema):
    class Meta:
        model = Admin


admin_schema = AdminSchema()
admins_schema = AdminSchema(many=True)


class TopicSchema(ModelSchema):
    class Meta:
        model = Topic


topic_schema = TopicSchema()
topics_schema = TopicSchema(many=True)

'''
class Channel(db.Model):
    __tablename__ = 'channels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    from_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    msg = db.relationship('Message', backref='msg', lazy=True)


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    from_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'))
'''
