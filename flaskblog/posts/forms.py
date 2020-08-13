from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    content = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Post')


class UpdatePostForm(FlaskForm):
    content = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Update Post')


class CommentForm(FlaskForm):
    message = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Comment')

class CommentsForm(FlaskForm):
    message = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Comment')


class ReplyForm(FlaskForm):
    message = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Reply')
