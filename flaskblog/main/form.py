from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class Searchform(FlaskForm):
    q= StringField(DataRequired())
    submit= SubmitField('Search', render_kw={'class': 'btn btn-success btn-block'})
