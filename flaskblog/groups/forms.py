from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import TextAreaField, SubmitField, FileField, StringField
from wtforms.validators import DataRequired


class TopicForm(FlaskForm):
    name = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Create')



class GroupPostForm(FlaskForm):
    content = TextAreaField(validators=[DataRequired()])
    #photo = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Post')



class SearchPostForm(FlaskForm):
    content = StringField('', validators=[DataRequired()])
    submit = SubmitField('Search Topics')

class CommentForm(FlaskForm):
    message = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Comment')