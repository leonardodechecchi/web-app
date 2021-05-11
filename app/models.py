from app import db, login_manager
from flask_login import UserMixin


from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_member(member_id):
    return Members.query.get(member_id)


class Persons(db.Model):
    __tablename__ = "Persons"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)


class Members(Persons):
    __tablename__ = "Members"
    persons = db.Column('Persons', db.ForeignKey('Persons.id'))
    social_number = db.Column(db.String(16), primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)

    def __init__(self, name, surname, social_number, email, password):
        super().__init__(name, surname)
        self.social_number = social_number
        self.email = email
        self.password = password

    def get_id(self):
        return self.social_number


"""
class Persons(db.Model):
    __tablename__ = "Persons"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    def __init__(self, name, surname):
        self.name = name
        self.surname = surname
class Members(Persons, UserMixin):
    __tablename__ = "Members"
    __table_args__ = {'extend_existing': True}
    social_number = db.Column(db.String(16), primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('Persons.id'))
    trainer_id = db.Column(db.Integer, db.ForeignKey('Trainers.id'))
    reservations = db.relationship('Reservations', backref='member', lazy=True)
    def __init__(self, name, surname, social_number, email, password):
        super().__init__(name, surname)
        self.social_number = social_number
        self.email = email
        self.password = password
    def __repr__(self):
        return f"Member('{self.social_number}', '{self.name}', '{self.surname}', '{self.email}')"
    # overriding get_id() : social_number it's our primary key
    def get_id(self):
        return self.social_number
class Staff(Persons):
    __tablename__ = "Staff"
    id = db.Column(db.Integer, db.ForeignKey('Persons.id'), primary_key=True)
    def __init__(self, name, surname):
        super().__init__(name, surname)
# Personal Trainers
class Trainers(Staff):
    __tablename__ = "Trainers"
    id = db.Column(db.Integer, db.ForeignKey('Staff.id'), primary_key=True)
    members = db.relationship('Members', backref='trainer', lazy=True)
class Managers(Staff):
    __tablename__ = "Managers"
    id = db.Column(db.Integer, db.ForeignKey('Staff.id'), primary_key=True)
# Courses
class Instructors(Staff):
    __tablename__ = "Instructors"
    id = db.Column(db.Integer, db.ForeignKey('Staff.id'), primary_key=True)
    courses = db.relationship('Courses', backref='instructor', lazy=True)
class Courses(db.Model):
    __tablename__ = "Courses"
    course_id = db.Column(db.Integer, db.ForeignKey('Instructors.id'), primary_key=True)
    name = db.Column(db.String(20))
    max_members = db.Column(db.Integer)
# Many to Many adds an association table between two classes. The association table is indicated by the
# relationship.secondary argument to relationship(). Usually, the Table uses the MetaData object associated with the
# declarative base class, so that the ForeignKey directives can locate the remote tables with which to link
class GymMachines(db.Model):
    __tablename__ = "GymMachines"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
class Equipments(db.Model):
    __tablename__ = "Equipments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
class Reservations(db.Model):
    __tablename__ = "Reservations"
    id = db.Column(db.String(16), db.ForeignKey('Members.social_number'), primary_key=True)
    # date
    # turn
class Schedules(db.Model):
    __tablename__ = "Schedules"
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date)
class Turns(db.Model):
    __tablename__ = "Turns"
    id = db.Column(db.Integer, primary_key=True)
    from_hour = db.Column(db.DateTime)
    to_hour = db.Column(db.DateTime)
"""