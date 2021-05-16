from datetime import time, date

from flask import render_template, url_for, flash, redirect

from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, EditProfileForm, Reservations
from app.models import Members, Courses, Turns, Schedules
from flask_login import login_user, current_user, logout_user, login_required
from wtforms import BooleanField


@app.route('/')
@app.route('/home')
def home():
    from_hour = time(9, 00, 00)
    to_hour = time(11, 00, 00)
    day = date(2021, 5, 26)
    turn = Turns(from_hour=from_hour, to_hour=to_hour)
    schedule = Schedules(day=day)
    db.session.add(turn)
    db.session.add(schedule)
    db.session.commit()
    for times in Turns.query.all():
        print(times.from_hour, times.to_hour)
    for dayz in Schedules.query.all():
        print(dayz.day)
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
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')  # hashing password
        # creating new member with the given data and hashed pw
        member = Members(name=form.name.data, surname=form.surname.data, social_number=form.social_number.data,
                         email=form.email.data, password=hashed_pw)
        db.session.add(member)  # adding member in the db
        db.session.commit()  # pushing changes
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
        member = Members.query.filter_by(email=form.email.data).first()  # querying member by email
        if member and bcrypt.check_password_hash(member.password,
                                                 form.password.data):  # if member exists and password is valid
            login_user(member, remember=form.remember.data)
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
        member = Members.query.filter_by(social_number=current_user.social_number).first()
        if form.name.data:
            member.name = form.name.data
        if form.surname.data:
            member.surname = form.surname.data
        if form.email.data:
            member.email = form.email.data
        if form.social_number.data:
            member.social_number = form.social_number.data
        if form.password.data:
            hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            member.password = hashed_pw
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('profile.html', title='Profile', user=current_user, form=form)


"""
@app.route('/calendar', methods=['GET', 'POST'])
@login_required
def calendar():
    # query che seleziona tutti i corsi in calendario
    courses = ["yoga", "crossfit", "cardio", "body", "gym"]

    class F(Prenotazioni):
        pass

    for name in courses:
        setattr(F, name, BooleanField())
    setattr(F, "submit", SubmitField('Confirm'))
    form = F()
    # courses = Courses.query(Courses.name)
    if form.is_submitted():
        for name in courses:
            print(getattr(form, name).data)
    return render_template('calendar.html', courses=courses, form=form, zip=zip)
"""


turns = [
    {
        'from_hour': '8.00',
        'to': '9.00'
    },
    {
        'from_hour': '9.00',
        'to': '10.00'
    },
    {
        'from_hour': '10.00',
        'to': '11.00'
    },
    {
        'from_hour': '11.00',
        'to': '12.00'
    },
    {
        'from_hour': '12.00',
        'to': '13.00'
    },
    {
        'from_hour': '13.00',
        'to': '14.00'
    }
]

days = [
    {'day': 'Monday'},
    {'day': 'Tuesday'},
    {'day': 'Wednesday'},
    {'day': 'Thursday'},
    {'day': 'Friday'},
    {'day': 'Saturday'}
]


@app.route('/calendar/gym', methods=['GET', 'POST'])
@login_required
def calendar_gym():
    class F(Reservations):
        pass
    for turn in turns:
        for day in days:
            setattr(F, turn['from_hour'] + day['day'], BooleanField('Reserve Now'))
    form = F()
    if form.is_submitted():
        for turn in turns:
            for day in days:
                print(getattr(form, turn['from_hour'] + day['day']).data)
    return render_template('calendar_gym.html', title='Gym Calendar',
                           turns=turns, days=days, form=form, getattr=getattr)


@app.route('/calendar/courses', methods=['GET', 'POST'])
@login_required
def calendar_courses():
    form = Reservations()
    courses = Courses.query.all()
    return render_template('calendar_courses.html', title='Courses Calendar',
                           turns=turns, num=1, range=range, form=form, courses=courses, zip=zip)
