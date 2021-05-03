from flask import render_template, url_for, flash, redirect
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/')
@app.route('/home')
def home():
    return render_template('public/home.html', title='Home Page')


@app.route('/about')
def about():
    return render_template('public/about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You must logout to make a new registration', 'info')
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')  # hashing password
        # creating new user with the given data and hashed pw
        user = User(social_number=form.social_number.data, name=form.name.data,
                    surname=form.surname.data, email=form.email.data, password=hashed_pw) 
        db.session.add(user)  # adding user in the db
        db.session.commit()  # pushing changes
        flash('Your account has been created! Now you are able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('public/register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged-in', 'info')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()  # querying user by email
        if user and bcrypt.check_password_hash(user.password, form.password.data):  # if user exists and password is valid
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash(f'Login Unsuccessful, please retry', 'danger')
    return render_template('public/login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/profile')
@login_required
def profile():
        return render_template('public/profile.html', title='Profile')