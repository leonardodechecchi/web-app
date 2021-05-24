from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TimeField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError

from app import bcrypt
from app.models import User


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


class CreateCourse(FlaskForm):
    name = StringField('Course Name', validators=[DataRequired()])
    max_members = IntegerField('Max Members Allowed', validators=[DataRequired()])
    schedule = DateField('Date', format='%d/%m/%Y', validators=[DataRequired()])
    turn_from_hour = TimeField('Start', format='%X', validators=[DataRequired()])
    turn_to_hour = TimeField('End', format='%X', validators=[DataRequired()])
    submit = SubmitField('Create')
