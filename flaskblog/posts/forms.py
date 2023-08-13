from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired
from wtforms import StringField, HiddenField
from wtforms.validators import DataRequired, Length

class PostForm(FlaskForm):
    content = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Post')


class UpdatePostForm(FlaskForm):
    content = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Update Post')

class CommentForm(FlaskForm):
    message = TextAreaField('Comment', validators=[DataRequired(), Length(max=500)])
    depth = HiddenField(default=0)  
    submit = SubmitField('Comment')

class ReplyForm(FlaskForm):
    content = StringField('Reply', validators=[DataRequired(), Length(max=500)])
    parent_id = HiddenField()  
    submit = SubmitField('Reply')
    
class CommentsForm(FlaskForm):
    message = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Comment')
