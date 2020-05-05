from flask_wtf import FlaskForm
from wtforms import StringField,  SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired




class PostForm(FlaskForm):
    content = TextAreaField( validators=[DataRequired()])
    submit = SubmitField('Post')




class UpdatePostForm(FlaskForm):
    content = TextAreaField( validators=[DataRequired()])
    submit = SubmitField('Update Post')


class CommentForm(FlaskForm):
    message = TextAreaField( validators=[DataRequired()])
    submit = SubmitField('Comment')



class ReplyForm(FlaskForm):
    replys = TextAreaField( validators=[DataRequired()])
    submit = SubmitField('Comment')