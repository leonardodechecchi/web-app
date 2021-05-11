from app import db, login_manager
from flask_login import UserMixin


# call-back
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Person(db.Model):
    __abstract__ = True
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)

    def __init__(self, name, surname):
        self.name = name
        self.surname = surname


class User(Person, UserMixin):
    __tablename__ = 'User'
    __table_args__ = {'extend_existing': True}
    social_number = db.Column(db.String(16), primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('Trainer.id'))

    def __init__(self, social_number, name, surname, email, password):
        super().__init__(name, surname)
        self.social_number = social_number
        self.email = email
        self.password = password

    def __repr__(self):
        return f"User('{self.social_number}', '{self.name}', '{self.surname}', '{self.email}')"

    # overriding get_id() : social_number it's our primary key 
    def get_id(self):
        return self.social_number


class Trainer(Person):
    __tablename__ = 'Trainer'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    users = db.relationship('User', backref='trainer', lazy=True)

    def __repr__(self):
        return f"Personal Trainer('{self.id}', '{self.name}', '{self.surname}')"
