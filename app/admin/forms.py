from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateField, TimeField
from wtforms.validators import DataRequired, ValidationError

from app.models import Courses


class CreateCourse(FlaskForm):
    name = StringField('Course Name', validators=[DataRequired()])
    max_members = IntegerField('Max Members Allowed', validators=[DataRequired()])
    submit = SubmitField('Create')

    def validate_name(self, name):
        course = Courses.query.filter_by(name=name.data).first()
        if course:
            raise ValidationError('That course already exists')


class AddEventCourse(FlaskForm):
    name = StringField('Course Name', validators=[DataRequired()])
    date = DateField('Date (yyyy-mm-dd)', validators=[DataRequired()])
    turn_start = TimeField('Course Start (hh:mm)', validators=[DataRequired()])
    turn_end = TimeField('Course End (hh:mm)', validators=[DataRequired()])
    submit = SubmitField('Insert')

    def validate_name(self, name):
        course = Courses.query.filter_by(name=name.data).first()
        if not course:
            raise ValidationError('That course does not exist. Please insert an existing course')


class CreateWeightRoom(FlaskForm):
    max_members = IntegerField('Max Members Allowed', validators=[DataRequired()])
    dimension = IntegerField('Dimension of the room in square meters', validators=[DataRequired()])
    submit = SubmitField('Create')


class AddEventGym(FlaskForm):
    date = DateField('Date (yyyy-mm-dd)', validators=[DataRequired()])
    turn_start = TimeField('Turn Start (hh:mm)', validators=[DataRequired()])
    turn_end = TimeField('Turn End (hh:mm)', validators=[DataRequired()])
    submit = SubmitField('Insert')
