from flask_app import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', back_populates='role')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    points = db.Column(db.Integer, default=0)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', back_populates='users')
    predictions = db.relationship('Prediction', back_populates='user')
    
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Race(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meeting_key = db.Column(db.Integer, unique=True, nullable=False)
    race_name = db.Column(db.String(100), nullable=False)
    race_date = db.Column(db.DateTime, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    predictions = db.relationship('Prediction', back_populates='race')

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    p1 = db.Column(db.String(50), nullable=False)
    p2 = db.Column(db.String(50), nullable=False)
    p3 = db.Column(db.String(50), nullable=False)
    last_place = db.Column(db.String(50), nullable=False)
    dnf = db.Column(db.String(50), nullable=False)
    fastest_lap = db.Column(db.String(50), nullable=False)
    team_podium = db.Column(db.String(50), nullable=False)
    team_most_points = db.Column(db.String(50), nullable=False)
    safety_car = db.Column(db.String(3), nullable=False)  # 'yes' or 'no'
    red_flag = db.Column(db.String(3), nullable=False)    # 'yes' or 'no'
    wet_race = db.Column(db.String(3), nullable=False)    # 'yes' or 'no'
    points_earned = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='predictions')
    race = db.relationship('Race', back_populates='predictions')

class RaceSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    round = db.Column(db.Integer, nullable=False)
    race_name = db.Column(db.String(100), nullable=False)
    circuit_name = db.Column(db.String(100), nullable=False)
    circuit_location = db.Column(db.String(100), nullable=False)
    circuit_country = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    time = db.Column(db.String(8), nullable=False)  # Store as "HH:MM:SS"
    fp1_date = db.Column(db.DateTime, nullable=True)
    fp1_time = db.Column(db.String(8), nullable=True)
    fp2_date = db.Column(db.DateTime, nullable=True)
    fp2_time = db.Column(db.String(8), nullable=True)
    fp3_date = db.Column(db.DateTime, nullable=True)
    fp3_time = db.Column(db.String(8), nullable=True)
    qualifying_date = db.Column(db.DateTime, nullable=True)
    qualifying_time = db.Column(db.String(8), nullable=True)
    sprint_date = db.Column(db.DateTime, nullable=True)
    sprint_time = db.Column(db.String(8), nullable=True)
    sprint_qualifying_date = db.Column(db.DateTime, nullable=True)
    sprint_qualifying_time = db.Column(db.String(8), nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RaceSchedule {self.year} Round {self.round}: {self.race_name}>"

    @property
    def race_datetime(self):
        """Combine date and time into a single datetime object"""
        if self.date and self.time:
            return datetime.combine(self.date.date(), datetime.strptime(self.time, "%H:%M:%S").time())
        return None

    @property
    def is_upcoming(self):
        """Check if the race is in the future"""
        return self.race_datetime and self.race_datetime > datetime.now(timezone.utc)

    @property
    def is_completed(self):
        """Check if the race has been completed"""
        return self.race_datetime and self.race_datetime < datetime.now(timezone.utc)