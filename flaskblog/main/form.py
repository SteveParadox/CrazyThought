from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired




from flask_wtf import FlaskForm
from wtforms import StringField,  SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class Searchform(FlaskForm):
    q= TextAreaField(DataRequired())
    submit= SubmitField('Search')


class PostForm(FlaskForm):
    content = TextAreaField( validators=[DataRequired()])
    photo = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])

    submit = SubmitField('Post')



class SharePostForm(FlaskForm):
    content = TextAreaField()

    submit = SubmitField('Share Post')

class GetPostForm(FlaskForm):
    content = TextAreaField( validators=[DataRequired()])
