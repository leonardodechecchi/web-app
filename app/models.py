from functools import wraps

from app import db, login_manager
from flask_login import UserMixin, current_user


# Call-back
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


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
    courses = db.relationship('Courses', backref='user', passive_deletes=True, lazy=True)
    reservations = db.relationship('Reservations', backref='user', passive_deletes=True, lazy=True)

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


class Reservations(db.Model):
    __tablename__ = "Reservations"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    # ForeignKey
    user_id = db.Column(db.String, db.ForeignKey('User.social_number', ondelete='CASCADE'))
    schedule_course_id = db.Column(db.Integer, db.ForeignKey('SchedulesCourse.id', ondelete='CASCADE'))
    schedule_weightroom_id = db.Column(db.Integer, db.ForeignKey('SchedulesWeightRoom.id', ondelete='CASCADE'))


class SchedulesCourse(db.Model):
    __tablename__ = "SchedulesCourse"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    # SchedulesCourse information
    day = db.Column(db.DATE, nullable=False)
    from_hour = db.Column(db.TIME, nullable=False)
    to_hour = db.Column(db.TIME, nullable=False)

    # Relationships
    reservations = db.relationship('Reservations', backref='schedules_course', passive_deletes=True, lazy=True)

    # ForeignKey
    course_id = db.Column(db.Integer, db.ForeignKey('Courses.id', ondelete='CASCADE'))


class Courses(db.Model):
    __tablename__ = "Courses"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    # Courses information
    name = db.Column(db.String(20), nullable=False)
    max_members = db.Column(db.Integer)

    # Relationships
    schedules_course = db.relationship('SchedulesCourse', backref='course', passive_deletes=True, lazy=True)

    # ForeignKey
    instructor_id = db.Column(db.String, db.ForeignKey('User.social_number', ondelete='CASCADE'))

    def __init__(self, name, max_members):
        self.name = name
        self.max_members = max_members


class SchedulesWeightRoom(db.Model):
    __tablename__ = "SchedulesWeightRoom"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    # SchedulesWeightRoom information
    day = db.Column(db.DATE, nullable=False)
    from_hour = db.Column(db.TIME, nullable=False)
    to_hour = db.Column(db.TIME, nullable=False)

    # Relationships
    reservations = db.relationship('Reservations', backref='schedules_weightroom', passive_deletes=True, lazy=True)

    # ForeignKey
    weightroom_id = db.Column(db.Integer, db.ForeignKey('WeightRooms.id', ondelete='CASCADE'))


class WeightRooms(db.Model):
    __tablename__ = "WeightRooms"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    # WeightRooms information
    dimension = db.Column(db.Float)
    max_members = db.Column(db.Integer)

    # Relationships
    schedules_weightroom = db.relationship('SchedulesWeightRoom', backref='weightroom', passive_deletes=True, lazy=True)

    def __init__(self, dimension, max_members):
        self.max_members = max_members
        self.dimension = dimension


if __name__ == '__main__':
    db.create_all()
