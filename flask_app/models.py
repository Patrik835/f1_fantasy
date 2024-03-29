from flask_app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
#create users model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(35), nullable=False, unique=True)
    email = db.Column(db.String(70), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    points = db.Column(db.Integer, default=0)
    quiz_answers = db.relationship('QuizAnswers', backref='user', lazy=True)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')
#create a password setter
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
#create a quiz answers model
class QuizAnswers(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True, nullable=False)
    q1 = db.Column(db.String(255), nullable=False)
    q2 = db.Column(db.String(255), nullable=False)
    q3 = db.Column(db.String(255), nullable=False)
    q4 = db.Column(db.String(255), nullable=False)
    q5 = db.Column(db.String(255), nullable=False)
    q6 = db.Column(db.String(255), nullable=False)
    q7 = db.Column(db.String(255), nullable=False)
    q8 = db.Column(db.String(255), nullable=False)
    q9 = db.Column(db.String(255), nullable=False)
    q10 = db.Column(db.String(255), nullable=False)
    q11 = db.Column(db.String(255), nullable=False)
    q12 = db.Column(db.String(255), nullable=False)
#create a quiz answers history model
class QuizAnswersHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    previous_race = db.Column(db.String(255), nullable=False)
    race_nr = db.Column(db.Integer, nullable=False)
    q1 = db.Column(db.String(255), nullable=False)
    q2 = db.Column(db.String(255), nullable=False)
    q3 = db.Column(db.String(255), nullable=False)
    q4 = db.Column(db.String(255), nullable=False)
    q5 = db.Column(db.String(255), nullable=False)
    q6 = db.Column(db.String(255), nullable=False)
    q7 = db.Column(db.String(255), nullable=False)
    q8 = db.Column(db.String(255), nullable=False)
    q9 = db.Column(db.String(255), nullable=False)
    q10 = db.Column(db.String(255), nullable=False)
    q11 = db.Column(db.String(255), nullable=False)
    q12 = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    points_for_race = db.Column(db.Integer, default=0)