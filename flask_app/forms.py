from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, ValidationError
from wtforms.validators import InputRequired, Length, EqualTo, Email
from flask_app.models import User

class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[InputRequired(), Length(min=3, max=15)])
    password = PasswordField("Password:", validators=[InputRequired(), Length(min=4, max=50)])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Username:", validators=[InputRequired(), Length(min=3, max=15)])
    email = StringField("Email:", validators=[InputRequired(), Email(), Length(min=4, max=50)])
    password = PasswordField("Password:", validators=[InputRequired(), Length(min=4, max=50), 
                                                    EqualTo('repeatpassword', message='Passwords must match')])
    repeatpassword = PasswordField("Repeat Password:", validators=[InputRequired(), Length(min=4, max=50)])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class PredictionForm(FlaskForm):
    # Driver choices will be populated dynamically from the API
    p1 = SelectField('1. Who will win the race?', coerce=str, validators=[InputRequired()])
    p2 = SelectField('2. Who will finish P2 (2nd place)?', coerce=str, validators=[InputRequired()])
    p3 = SelectField('3. Who will finish P3 (3rd place)?', coerce=str, validators=[InputRequired()])
    last_place = SelectField('4. Who will finish last?', coerce=str, validators=[InputRequired()])
    dnf = SelectField('5. Who will DNF?', coerce=str, validators=[InputRequired()])
    fastest_lap = SelectField('6. Who will get the fastest lap?', coerce=str, validators=[InputRequired()])
    
    # Yes/No predictions
    safety_car = SelectField('7. Will there be a Safety Car?', 
                           choices=[('yes', 'Yes'), ('no', 'No')],
                           validators=[InputRequired()])
    red_flag = SelectField('8. Will there be a Red Flag?',
                          choices=[('yes', 'Yes'), ('no', 'No')],
                          validators=[InputRequired()])
    wet_race = SelectField('9. Will it be a Wet Race?',
                          choices=[('yes', 'Yes'), ('no', 'No')],
                          validators=[InputRequired()])
    
    # Team predictions
    team_podium = SelectField('10. Which team will have two drivers on the podium?', coerce=str, validators=[InputRequired()])
    team_most_points = SelectField('11. Which team will score the most points?', coerce=str, validators=[InputRequired()])
    
    submit = SubmitField("Submit Predictions")

class AdminUserForm(FlaskForm):
    username = StringField("Username:", validators=[InputRequired()])
    email = StringField("Email:", validators=[InputRequired(), Email()])
    role = SelectField("Role:", coerce=int, validators=[InputRequired()])
    submit = SubmitField("Update User")
    