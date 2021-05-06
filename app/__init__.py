from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from app.config import DATABASE_URI

app = Flask(__name__)
app.config['SECRET_KEY'] = '5fd9b065b5a8ec13542a15bf09a7d92e'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # necessary for login_required
login_manager.login_message_category = 'info'  # info : bootstrap class (blue text)

from app import routes