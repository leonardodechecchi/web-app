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

def __repr__(self):
    return f"User('{self.social_number}', '{self.name}', '{self.surname}', '{self.email}')"

#overriding get_id() : social_number it's our primary key
def get_id(self):
        return self.social_number

def load_user(persona_id):
    return User.query.get(persona_id)

class persone(db.Model):
    __tablename__ = "persone"
    idpersona = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(30))
    cognome = db.Column(db.String(30))
    codice_fiscale = db.Column(db.String(16))
    email = db.Column(db.String(30))

class iscritti(db.Model):
    __tablename__ = "iscritti"
    id_iscritto = db.Column(db.Integer, db.ForeignKey('persone.idpersona'), primary_key=True)

class istruttori(db.Model):
    __tablename__ = "istruttori"
    id_istruttore = db.Column(db.Integer, db.ForeignKey('persone.idpersona'), primary_key=True)

class personal_trainer(db.Model):
    __tablename__ = "personal_trainer"
    id_pt = db.Column(db.Integer, db.ForeignKey('persone.idpersona'), primary_key=True)

class dirigenti(db.Model):
    __tablename__ = "dirigenti"
    id_dirigente = db.Column(db.Integer, db.ForeignKey('persone.idpersona'), primary_key=True)

class corsi(db.Model):
    __tablename__ = "corsi"
    id_corso = db.Column(db.Integer, primary_key=True)
    id_istruttore = db.Column(db.Integer, db.ForeignKey('istruttori.id_istruttore'))
    nome = db.Column(db.String(20))
    max_posti = db.Column(db.Integer)

class prenotazioni(db.Model):
    __tablename__ = "prenotazioni"
    id_prenotazione = db.Column(db.Integer, primary_key=True)
    id_iscritto = db.Column(db.Integer, db.ForeignKey('iscritti.id_iscritto'))

class pianificazioni(db.Model):
    __tablename__ = "pianificazioni"
    id_piano = db.Column(db.Integer, primary_key=True)
    giorno = db.Column(db.Date)

class turni(db.Model):
    __tablename__ = "turni"
    id_turno = db.Column(db.Integer, primary_key=True)
    da = db.Column(db.DateTime)
    a = db.Column(db.DateTime)

#if __name__ == '__main__':
db.create_all()
