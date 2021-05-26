from app import bcrypt, db
from app.models import User

if __name__ == '__main__':
    social_number = '12345678123456'
    name = 'admin'
    surname = 'admin'
    email = 'admin@example.com'
    password = 'admin'
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    admin = User(social_number=social_number, name=name, surname=surname, email=email, password=hashed_pw,
                 role='instructor')
    db.session.add(admin)
    db.session.commit()
