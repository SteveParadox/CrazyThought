from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import TextAreaField, SubmitField, FileField, StringField
from wtforms.validators import DataRequired, Length
from wtforms import StringField, HiddenField


class TopicForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    submit = SubmitField('Create')


class GroupPostForm(FlaskForm):
    content = TextAreaField(validators=[DataRequired()])
    #photo = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Post')


class SearchPostForm(FlaskForm):
    content = StringField('', validators=[DataRequired()])
    submit = SubmitField('Search Topics')

class GroupCommentForm(FlaskForm):
    message = TextAreaField(validators=[DataRequired()])
    depth = HiddenField(default=0) 
    submit = SubmitField('Comment')

class GroupReplyForm(FlaskForm):
    content = StringField('Reply', validators=[DataRequired(), Length(max=500)])
    parent_id = HiddenField()  
    submit = SubmitField('Reply')
    