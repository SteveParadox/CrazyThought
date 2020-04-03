from flask_wtf import FlaskForm
from wtforms import StringField,  SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed



class PostForm(FlaskForm):
    content = TextAreaField( validators=[DataRequired()])
    photo = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])

    submit = SubmitField('Post')




class UpdatePostForm(FlaskForm):
    content = TextAreaField( validators=[DataRequired()])
    photo = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])

    submit = SubmitField('Update Post')

