from flask import render_template, url_for, flash, redirect
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, EditProfileForm, ReservationForm
from app.models import User, Role, Course, Turn, Schedule
from flask_login import login_user, current_user, logout_user, login_required
from wtforms import BooleanField
from flask_user import roles_required


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home Page')


@app.route('/about')
def about():
    return render_template('about-us.html', title='About Us')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You must logout to make a new registration', 'info')
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # hashing password
        user = User(name=form.name.data, surname=form.surname.data, social_number=form.social_number.data,
                    email=form.email.data, password=hashed_pw)
        user.roles.append(Role(name='Member'))
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! Now you are able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged-in', 'info')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data):  # if user exists and password is valid
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash(f'Login Unsuccessful, please retry', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
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
        return redirect(url_for('home'))
    return render_template('profile.html', title='Profile', user=current_user, form=form)


@app.route('/calendar/gym', methods=['GET', 'POST'])
@login_required
def calendar_gym():
    turns = Turn.query.distinct(Turn.from_hour, Turn.to_hour)
    schedules = Schedule.query.all()

    class F(ReservationForm):
        pass

    # init F
    for turn in turns:
        for schedule in schedules:
            setattr(F, str(turn.from_hour) + str(schedule.day), BooleanField('Reserve Now'))

    form = F()
    if form.validate_on_submit():
        for turn in turns:
            for schedule in schedules:
                if getattr(form, str(turn.from_hour) + str(schedule.day)).data:
                    pass  # TODO if checked

    return render_template('calendar_gym.html', title='Gym Calendar',
                           turns=turns, schedules=schedules, form=form, getattr=getattr, str=str, Schedule=Schedule)


@app.route('/calendar/courses', methods=['GET', 'POST'])
@login_required
def calendar_courses():
    turns = Turn.query.all()
    form = ReservationForm()
    courses = Course.query.all()
    return render_template('calendar_courses.html', title='Course Calendar',
                           turns=turns, num=1, range=range, form=form, courses=courses, zip=zip)
