from app import db, bcrypt
from app.models import User

name = 'admin'
surname = 'admin'
social_number = 'VSCCLT08P65A662L'
email = 'admin@example.com'
password = 'admin'
hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

user = User(name=name, surname=surname, social_number=social_number, email=email, password=hashed_pw, role='instructor')
db.session.add(user)
db.session.commit()
