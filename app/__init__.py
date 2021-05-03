from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '5fd9b065b5a8ec13542a15bf09a7d92e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # relative location
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from app import routes