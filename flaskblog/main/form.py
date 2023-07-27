from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired


class TopicForm(FlaskForm):
    name = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Create')


class Searchform(FlaskForm):
    livebox = StringField(DataRequired())
    submit = SubmitField('Search')


class PostForm(FlaskForm):
    content = TextAreaField(validators=[DataRequired()])
    photo = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Post')


class PhotoForm(FlaskForm):
    photo = FileField('', validators=[FileAllowed(['jpg', 'png']), DataRequired()])
    submit = SubmitField('Upload')


class VideoForm(FlaskForm):
    video = FileField('', validators=[FileAllowed(['mp4', 'webm']), DataRequired()])
    submit = SubmitField('Upload video')


class SharePostForm(FlaskForm):
    content = TextAreaField()
    submit = SubmitField('Share Post')


class GetPostForm(FlaskForm):
    content = TextAreaField(validators=[DataRequired()])
