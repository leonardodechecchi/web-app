from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import current_user, login_user, logout_user, login_required

from app import bcrypt, db
from app.models import User, requires_roles
from app.users.forms import RegistrationForm, LoginForm, EditProfileForm

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You must logout to make a new registration', 'info')
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, surname=form.surname.data, social_number=form.social_number.data,
                    email=form.email.data, password=hashed_pw, role='member')
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! Now you are able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged-in', 'info')
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data):  # if user exists and password is valid
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.home'))
        else:
            flash(f'Login Unsuccessful, please retry', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/profile', methods=['GET', 'POST'])
@login_required
@requires_roles('member')
def profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        user = User.query.filter_by(social_number=current_user.social_number).first()
        if form.name.data:
            user.name = form.name.data
        if form.surname.data:
            user.surname = form.surname.data
        if form.email.data:
            user.email = form.email.data
        if form.social_number.data:
            user.social_number = form.social_number.data
        if form.password.data:
            hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_pw
        db.session.commit()
        flash('Profile has been successfully edited', 'success')
        return redirect(url_for('main.home'))
    return render_template('profile.html', title='Profile', user=current_user, form=form)
