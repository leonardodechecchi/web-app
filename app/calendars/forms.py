from flask_wtf import FlaskForm
from wtforms import SubmitField


class CalendarForm(FlaskForm):
    submit = SubmitField('Reserve Now')
