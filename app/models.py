from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_member(member_social_number):
    return Members.query.get(member_social_number)


class Persons(db.Model, UserMixin):
    __tablename__ = "Persons"
    __table_args__ = {'extend_existing': True}
    social_number = db.Column(db.String(16), primary_key=True)
    type = db.Column(db.String(50))  # discriminator
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
    trainer_id = db.Column(db.String(16), db.ForeignKey('Trainers.social_number'))

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


class Staff(Persons):
    __tablename__ = "Staff"
    __table_args__ = {'extend_existing': True}
    social_number = db.Column(db.String(16), db.ForeignKey('Persons.social_number'), primary_key=True)
    role = db.Column(db.String(30))

    def __init__(self, name, surname, role):
        super().__init__(name, surname)
        self.role = role

    __mapper_args__ = {
        'polymorphic_identity': 'Staff'
    }


class Trainers(Staff):
    __tablename__ = "Trainers"
    __table_args__ = {'extend_existing': True}
    social_number = db.Column(db.String(16), db.ForeignKey('Staff.social_number'), primary_key=True)
    members = db.relationship('Members', backref='trainer', lazy=True)

    __mapper_args__ = {
        'polymorphic_identity': 'Trainers'
    }


class Managers(Staff):
    __tablename__ = "Managers"
    __table_args__ = {'extend_existing': True}
    social_number = db.Column(db.String(16), db.ForeignKey('Staff.social_number'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'Managers'
    }


class Instructors(Staff):
    __tablename__ = "Instructors"
    __table_args__ = {'extend_existing': True}
    social_number = db.Column(db.String(16), db.ForeignKey('Staff.social_number'), primary_key=True)
    courses = db.relationship('Courses', backref='instructor', lazy=True)

    __mapper_args__ = {
        'polymorphic_identity': 'Instructors'
    }


class Courses(db.Model):
    __tablename__ = "Courses"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    max_members = db.Column(db.Integer)
    instructor_id = db.Column(db.String, db.ForeignKey('Instructors.social_number'), nullable=False)

    def __init__(self, name, max_members):
        self.name = name
        self.max_members = max_members


""""
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

if __name__ == '__main__':
    db.create_all()

