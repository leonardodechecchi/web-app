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
login_manager.login_view = 'users.login'  # necessary for login_required
login_manager.login_message_category = 'info'  # info : bootstrap class (blue text)

from app.admin.routes import admin
from app.calendars.routes import calendars
from app.main.routes import main
from app.users.routes import users

app.register_blueprint(admin)
app.register_blueprint(calendars)
app.register_blueprint(main)
app.register_blueprint(users)
