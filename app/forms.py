from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError

from app import bcrypt
from app.models import Members


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    surname = StringField('Surname', validators=[DataRequired(), Length(min=2, max=20)])
    social_number = StringField('Social Security Number', validators=[DataRequired(), Length(min=16, max=16)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    # constraints
    def validate_email(self, email):
        member = Members.query.filter_by(email=email.data).first()
        if member:
            raise ValidationError('That email is taken. Please choose another one')

    def validate_social_number(self, social_number):
        member = Members.query.filter_by(social_number=social_number.data).first()
        if member:
            raise ValidationError('That social number security already exists. You are already registered')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')  # allow users to stay logged in for some time
    submit = SubmitField('Login')


class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=20)])
    surname = StringField('Surname', validators=[Length(max=20)])
    social_number = StringField('Social Security Number', validators=[Length(min=16, max=16)])
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    oldpassword = PasswordField('Old Password', validators=[DataRequired()])
    submit = SubmitField('Update')

    # constraints
    def validate_email(self, email):
        if email:
            member = Members.query.filter(Members.email == email.data, Members.email != current_user.email).first()
            if member:
                raise ValidationError('That email is taken. Please choose another one')

    def validate_social_number(self, social_number):
        if social_number:
            member = Members.query.filter(Members.social_number == social_number.data,
                                          Members.social_number != current_user.social_number).first()
            if member:
                raise ValidationError('That social number security already exists. You are already registered')

    def validate_oldpassword(self, oldpassword):
        member = Members.query.filter_by(social_number=current_user.social_number).first()
        if not bcrypt.check_password_hash(member.password, oldpassword.data):
            raise ValidationError('Wrong password')


class Prenotazioni(FlaskForm):
    pass
