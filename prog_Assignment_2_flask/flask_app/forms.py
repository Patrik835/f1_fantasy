from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, ValidationError
from wtforms.validators import InputRequired, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField("Select your username:", validators=[InputRequired(), Length(min=3, max=15)])
    password = PasswordField("Select your password:", validators=[InputRequired(), Length(min=4, max=50)])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Select your username:", validators=[InputRequired(), Length(min=3, max=15)])
    email = StringField("Write your email:", validators=[InputRequired(), Length(min=4, max=50)])
    password = PasswordField("Select your password:", validators=[InputRequired(), Length(min=4, max=50),EqualTo('repeatpassword', message='Passwords must match')])
    repeatpassword = PasswordField("Repeat your password:", validators=[InputRequired(), Length(min=4, max=50)])
    submit = SubmitField("Register")
    
class QuizForm(FlaskForm):
    drivers = [('ver','Max Verstappen'),('per','Sergio Perez'),('ham','Lewis Hamilton'),
               ('rus','George Russel'),('nor','Lando Norris'),('pia','Oskar Piastry'),
               ('lec','Charles Leclerc'),('sai','Carlos Sainz'),('gas','Pierre Gasly'),
               ('oco','Esteban Ocon'),('alo','Fernando Alonso'),('str','Lance Stroll'),
               ('mag','Kevin Magnussen'),('hul','Nico Hulkenberg'),('bot','Valtteri Bottas'),
               ('zho','Guanyu Zhou'),('tsu','Yuki Tsunoda'),('vri','Nyck de Vries'),
               ('alb','Alex Albon'),('sar','Logan Sargeant')]
    teams = [('red','Red Bull'),('mer','Mercedes'),('fer','Ferrari'),('ast','Aston Martin'),('alp','Alpine'),
             ('mcl','McLaren'),('art','Alpha Romeo'),('atr','Alpha Tauri'),('has','Haas'),('wil','Williams')]
    y_and_n = [('unanswered','No answer'),('yes','Yes'),('no','No')]
    q1 = SelectField('Who will win the race?', choices=drivers )
    q2 = SelectField('Who will finish P2 (2nd place)?', choices=drivers )
    q3 = SelectField('Who will achieve the fastest lap of the race?', choices=drivers)
    q4 = SelectField('Who will finish on the last place of the drivers that succesfully ended the race?', choices=drivers)
    q5 = SelectField('Who wont finish the race (DNF)?', choices=drivers)
    q6 = SelectField('Will there be a red flag in the race', choices= y_and_n)
    q7 = SelectField('Will there be a safety car in the race', choices= y_and_n)
    q8 = SelectField('Will some driver get a penalty?', choices= y_and_n)
    q9 = SelectField('Will the driver starting from the pole position (P1) win?', choices= y_and_n)
    q10 = SelectField('Will there be two drivers of the same team on the podium (which team)?', choices = teams)
    q11 = SelectField('Team with the most points after this race? (team name)', choices = teams)
    submit = SubmitField("Submit")
    