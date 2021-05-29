import enum
from functools import wraps

from app import db, login_manager, bcrypt
from flask_login import UserMixin, current_user


# Call-back
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = "User"
    __table_args__ = {'extend_existing': True}

    # User primary_key
    social_number = db.Column(db.String(16), primary_key=True)

    # User information
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)

    # User authentication information
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(64), default='member')

    # Relationship
    courses = db.relationship('Course', backref='user', passive_deletes=True, lazy=True)

    def __init__(self, social_number, name, surname, email, password, role):
        self.social_number = social_number
        self.name = name
        self.surname = surname
        self.email = email
        self.password = password
        self.role = role

    def __repr__(self):
        return f"User('{self.social_number}', '{self.name}', '{self.surname}', '{self.email}', '{self.roles}')"

    def get_id(self):
        return self.social_number


def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                # Redirect the user to an unauthorized notice!
                return "You are not authorized to access this page"
            return f(*args, **kwargs)
        return wrapped
    return wrapper


class Schedule(db.Model):
    __tablename__ = "Schedule"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    # Schedule information
    day = db.Column(db.DATE, nullable=False, unique=True)

    # Relationships
    courses = db.relationship('Course', secondary='ScheduleCourse', backref=db.backref('schedules', lazy='dynamic'))
    weightrooms = db.relationship('WeightRoom', secondary='ScheduleWeightRoom', backref=db.backref('weightrooms',
                                  lazy='dynamic'))

    def __init__(self, day):
        self.day = day

    def __repr__(self):
        return f"Schedule('{self.day}')"


class ScheduleCourse(db.Model):
    __tablename__ = "ScheduleCourse"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    # Turn information
    from_hour = db.Column(db.TIME, nullable=False)
    to_hour = db.Column(db.TIME, nullable=False)

    # ForeignKey
    schedule_id = db.Column(db.Integer, db.ForeignKey('Schedule.id', ondelete='CASCADE'))
    course_id = db.Column(db.Integer, db.ForeignKey('Course.id', ondelete='CASCADE'))


class ScheduleWeightRoom(db.Model):
    __tablename__ = "ScheduleWeightRoom"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    # Turn information
    from_hour = db.Column(db.TIME, nullable=False)
    to_hour = db.Column(db.TIME, nullable=False)

    # ForeignKey
    schedule_id = db.Column(db.Integer, db.ForeignKey('Schedule.id', ondelete='CASCADE'))
    weightroom_id = db.Column(db.Integer, db.ForeignKey('WeightRoom.id', ondelete='CASCADE'))


class Course(db.Model):
    __tablename__ = "Course"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    # Course information
    name = db.Column(db.String(20), nullable=False)
    max_members = db.Column(db.Integer)

    # ForeignKey
    instructor_id = db.Column(db.String, db.ForeignKey('User.social_number', ondelete='CASCADE'))

    # Relationships
    # schedules = db.relationship('Schedule', secondary='ScheduleCourse', back_populates='courses', lazy='dynamic')

    def __init__(self, name, max_members):
        self.name = name
        self.max_members = max_members


class WeightRoom(db.Model):
    __tablename__ = "WeightRoom"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    # WeightRoom information
    dimension = db.Column(db.Float)
    max_members = db.Column(db.Integer)

    # Relationships schedules = db.relationship('Schedule', secondary='ScheduleWeightRoom',
    # back_populates='weightrooms', lazy='dynamic')

    def __init__(self, dimension, max_members):
        self.max_members = max_members
        self.dimension = dimension


if __name__ == '__main__':
    db.create_all()
