from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '5fd9b065b5a8ec13542a15bf09a7d92e'


@app.route('/')
@app.route('/home')
def home():
    return render_template('public/home.html', title='Home Page')


@app.route('/about')
def about():
    return render_template('public/about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():  # if form validated after submit
        flash(f'Account created for {form.username.data}', 'success')
        return redirect(url_for('home'))
    return render_template('public/register.html', title='Register', form=form)


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('public/login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(debug=True)
