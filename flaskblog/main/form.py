from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class Searchform(FlaskForm):
    q= StringField(DataRequired())
    submit= SubmitField('Search', render_kw={'class': 'btn btn-success btn-block'})

from flask_wtf import FlaskForm
from wtforms import StringField,  SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed



class PostForm(FlaskForm):
    content = TextAreaField( validators=[DataRequired()])
    photo = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])

    submit = SubmitField('Post')



class SharePostForm(FlaskForm):
    content = TextAreaField()

    submit = SubmitField('Share Post')