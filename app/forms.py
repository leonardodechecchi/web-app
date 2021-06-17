from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TimeField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError

from app import bcrypt
from app.models import User, Courses, SchedulesCourse


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    surname = StringField('Surname', validators=[DataRequired(), Length(min=2, max=50)])
    social_number = StringField('Social Security Number', validators=[DataRequired(), Length(min=16, max=16)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    # Constraints
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose another one')

    def validate_social_number(self, social_number):
        user = User.query.filter_by(social_number=social_number.data).first()
        if user:
            raise ValidationError('That social number security already exists. You are already registered')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class EditProfileForm(RegistrationForm):
    oldpassword = PasswordField('Old Password', validators=[DataRequired()])
    submit = SubmitField('Update')

    # constraints
    def validate_email(self, email):
        if email:
            user = User.query.filter(User.email == email.data, User.email != current_user.email).first()
            if user:
                raise ValidationError('That email is taken. Please choose another one')

    def validate_social_number(self, social_number):
        if social_number:
            user = User.query.filter(User.social_number == social_number.data,
                                     User.social_number != current_user.social_number).first()
            if user:
                raise ValidationError('That social number security already exists. You are already registered')

    def validate_oldpassword(self, oldpassword):
        user = User.query.filter_by(social_number=current_user.social_number).first()
        if not bcrypt.check_password_hash(user.password, oldpassword.data):
            raise ValidationError('Wrong password')


class ReservationForm(FlaskForm):
    submit = SubmitField('Reserve Now')


class CancelReservationForm(FlaskForm):
    submit = SubmitField('Cancel Selected Reservations')


class CreateCourse(FlaskForm):
    name = StringField('Courses Name', validators=[DataRequired()])
    max_members = IntegerField('Max Members Allowed', validators=[DataRequired()])
    submit = SubmitField('Create')

    def validate_name(self, name):
        if name:
            course = Courses.query.filter_by(name=name.data).first()
            if course:
                raise ValidationError('That course already exists')


class AddEventCourse(FlaskForm):
    name = StringField('Courses Name', validators=[DataRequired()])
    date = DateField('Date (yyyy-mm-dd)')
    turn_start = TimeField('Courses Start (hh:mm)')
    turn_end = TimeField('Courses End (hh:mm)')
    submit = SubmitField('Insert')

    def validate_name(self, name):
        if name:
            course = Courses.query.filter_by(name=name.data).first()
            if not course:
                raise ValidationError('That course does not exist. Please insert an existing course')


class CreateWeightRoom(FlaskForm):
    max_members = IntegerField('Max Members Allowed', validators=[DataRequired()])
    dimension = IntegerField('Dimension of the room in square meters', validators=[DataRequired()])
    submit = SubmitField('Create')


class AddEventGym(FlaskForm):
    date = DateField('Date (yyyy-mm-dd)')
    turn_start = TimeField('Courses Start (hh:mm)')
    turn_end = TimeField('Courses End (hh:mm)')
    submit = SubmitField('Insert')
