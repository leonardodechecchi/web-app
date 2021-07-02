from flask import Blueprint, render_template

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    return render_template('home.html', title='Home Page')


@main.route('/about')
def about():
    return render_template('about-us.html', title='About Us')
