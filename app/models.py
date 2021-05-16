from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_member(member_id):
    return Members.query.get(member_id)


class Persons(db.Model, UserMixin):
    __tablename__ = "Persons"
    __table_args__ = {'extend_existing': True}
    social_number = db.Column(db.String(16), primary_key=True)
    type = db.Column(db.String(50))
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Persons',
        'polymorphic_on': type
    }

    def __init__(self, name, surname):
        self.name = name
        self.surname = surname

    def get_id(self):
        return self.social_number


class Members(Persons):
    __tablename__ = "Members"
    __table_args__ = {'extend_existing': True}
    social_number = db.Column(db.String(16), db.ForeignKey('Persons.social_number'), primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Members'
    }

    def __init__(self, name, surname, social_number, email, password):
        super().__init__(name, surname)
        self.social_number = social_number
        self.email = email
        self.password = password

    def __repr__(self):
        return f"Member('{self.social_number}', '{self.name}', '{self.surname}', '{self.email}')"

    def get_social_number(self):
        return self.social_number


class Staff(Persons):
    __tablename__ = "Staff"
    __table_args__ = {'extend_existing': True}
    social_number = db.Column(db.String(16), db.ForeignKey('Persons.social_number'), primary_key=True)
    role = db.Column(db.String(30), nullable=False)

    def __init__(self, name, surname, role):
        super().__init__(name, surname)
        self.role = role

    __mapper_args__ = {
        'polymorphic_identity': 'Staff'
    }


class Courses(db.Model):
    __tablename__ = "Courses"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    max_members = db.Column(db.Integer)

    def __init__(self, name, max_members):
        self.name = name
        self.max_members = max_members


scheduling = db.Table('scheduling',
                      db.Column('schedule_id', db.Integer, db.ForeignKey('Schedules.id')),
                      db.Column('turn_id', db.Integer, db.ForeignKey('Turns.id')), extend_existing=True)


class Schedules(db.Model):
    __tablename__ = "Schedules"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date, nullable=False)
    turns = db.relationship('Turns', secondary=scheduling, backref=db.backref('schedules', lazy='dynamic'))

    def __init__(self, day):
        self.day = day


class Turns(db.Model):
    __tablename__ = "Turns"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    from_hour = db.Column(db.Time, nullable=False)
    to_hour = db.Column(db.Time, nullable=False)

    def __init__(self, from_hour, to_hour):
        self.from_hour = from_hour
        self.to_hour = to_hour


if __name__ == '__main__':
    db.create_all()
    for user in Members.query.all():
        print(user.surname)
