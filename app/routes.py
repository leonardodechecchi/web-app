from flask import render_template, url_for, flash, redirect

from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, EditProfileForm, Reservations
from app.models import Members, Courses
from flask_login import login_user, current_user, logout_user, login_required


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
        'from': 8.00,
        'to': 9.00
    },
    {
        'from': 9.00,
        'to': 10.00
    },
    {
        'from': 10.00,
        'to': 11.00
    },
    {
        'from': 11.00,
        'to': 12.00
    },
    {
        'from': 12.00,
        'to': 13.00
    }
]


@app.route('/calendar/gym', methods=['GET', 'POST'])
@login_required
def calendar_gym():
    form = Reservations()
    return render_template('calendar_gym.html', title='Gym Calendar',
                           turns=turns, num=1, range=range, form=form)


@app.route('/calendar/courses', methods=['GET', 'POST'])
@login_required
def calendar_courses():
    form = Reservations()
    courses = Courses.query.all()
    return render_template('calendar_courses.html', title='Courses Calendar',
                           turns=turns, num=1, range=range, form=form, courses=courses)
