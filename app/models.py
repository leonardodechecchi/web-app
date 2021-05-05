from app import db, login_manager
from flask_login import UserMixin


# call-back
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = "User"
    __table_args__ = {'extend_existing': True}
    social_number = db.Column(db.String(16), primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)

    def __init__(self, social_number, name, surname, email, password):
        self.surname = surname
        self.email = email
        self.name = name
        self.social_number = social_number
        self.password = password

    def __repr__(self):
        return f"User('{self.social_number}', '{self.name}', '{self.surname}', '{self.email}')"

    # overriding get_id() : social_number it's our primary key 
    def get_id(self):
        return self.social_number


if __name__ == '__main__':
    db.create_all()
    for namen, surnamen, codicefiscalen, emailn, passwordn in db.session.query(User.name, User.surname,
                                                                               User.social_number,
                                                                               User.email, User.password):
        print(namen, surnamen, codicefiscalen, emailn, passwordn)
