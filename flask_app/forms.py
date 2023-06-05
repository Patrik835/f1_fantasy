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
    drivers = [('VER','Max Verstappen'),('PER','Sergio Perez'),('HAM','Lewis Hamilton'),
               ('RUS','George Russel'),('NOR','Lando Norris'),('PIA','Oscar Piastri'),
               ('LEC','Charles Leclerc'),('SAI','Carlos Sainz'),('GAS','Pierre Gasly'),
               ('OCO','Esteban Ocon'),('ALO','Fernando Alonso'),('STR','Lance Stroll'),
               ('MAG','Kevin Magnussen'),('HUL','Nico Hulkenberg'),('BOT','Valtteri Bottas'),
               ('ZHO','Guanyu Zhou'),('TSU','Yuki Tsunoda'),('DEV','Nyck de Vries'),
               ('ALB','Alex Albon'),('SAR','Logan Sargeant'),('nobody','Nobody')]
    teams = [('red_bull','Red Bull'),('mercedes','Mercedes'),('ferrari','Ferrari'),('aston_martin','Aston Martin'),('alpine','Alpine'),
             ('mclaren','McLaren'),('alfa','Alfa Romeo'),('alphatauri','Alpha Tauri'),('haas','Haas'),('williams','Williams')]
    y_and_n = [('unanswered','No answer'),('yes','Yes'),('no','No')]
    q1 = SelectField('1. Who will win the race?', choices=drivers )
    q2 = SelectField('2. Who will finish P2 (2nd place)?', choices=drivers )
    q3 = SelectField('3. Who will finish P3 (3rd place)?', choices=drivers)
    q4 = SelectField('4. Who will finish on the last place of the drivers that succesfully ended the race?', choices=drivers)
    q5 = SelectField('5. Who wont finish the race (DNF)?', choices=drivers)
    q6 = SelectField('6. Who will achieve the fastest lap of the race?', choices= drivers)
    q7 = SelectField('7. Will there be collision of two or more cars?', choices= y_and_n)
    q8 = SelectField('8. Will Lando Norris score points?', choices= y_and_n)
    q9 = SelectField('9. Will the driver starting from the pole position (P1) win?', choices= y_and_n)
    q10 = SelectField('10. Will there be two drivers of the same team on the podium (which team)?', choices = teams)
    q11 = SelectField('11. Team with the most points after this race? (team name)', choices = teams)
    q12 = StringField('12. In what lap will be the fastest lap achieved?', validators=[InputRequired(),Length(min=1, max=3)])
    submit = SubmitField("Submit")
    