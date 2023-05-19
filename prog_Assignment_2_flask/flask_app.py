from flask import Flask, render_template, send_from_directory, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, AnyOf
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# Create an instance of Flask
app = Flask(__name__)
#add database
#sqlite db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#secret key for forms
app.config['SECRET_KEY'] = "Thisisasecretkey"

db = SQLAlchemy(app)
app.app_context().push()

#create database model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(35), nullable=False, unique=True)
    email = db.Column(db.String(70), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
#create a string
    def __repr__(self):
        return '<Name %r>' % self.username

class LoginForm(FlaskForm):
    username = StringField("Select your username:", validators=[InputRequired(), Length(min=3, max=15)])
    password = PasswordField("Select your password:", validators=[InputRequired(), Length(min=4, max=50)])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Select your username:", validators=[InputRequired(), Length(min=3, max=15)])
    email = StringField("Write your email:", validators=[InputRequired(), Length(min=4, max=50)])
    password = PasswordField("Select your password:", validators=[InputRequired(), Length(min=4, max=50)])
    repeatpassword = PasswordField("Repeat your password:", validators=[InputRequired(), Length(min=4, max=50),EqualTo('password', message='Passwords must match')])
    submit = SubmitField("Register")


#create route that renders index.html template
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    username = None
    password = None
    form = LoginForm()
    #validate form
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        form.username.data = ""
        form.password.data = ""
        flash("You have successfully logged in")
    return render_template("login.html", username = username, password = password, form = form)

@app.route("/register", methods=["GET", "POST"])
def register():
    username = None
    email = None
    password = None
    repeatpassword = None
    form = RegisterForm()
    #validate form
    if form.password.data != form.repeatpassword.data:
        flash("Passwords must match try again")
    elif form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data, email=form.email.data).first()  # check if user exists
        if user is None:                                                                          # if not, create new user
            user = Users(username=form.username.data, email=form.email.data, password=form.password.data)  # create new user
            db.session.add(user)                # add new user to database
            db.session.commit()                 # commit changes to database
            flash("You have successfully registered")
        else:
            flash("Username or email already exists")
        username = form.username.data
        email = form.email.data
        password = form.password.data
        repeatpassword = form.repeatpassword.data
        form.username.data = ""
        form.email.data = ""
        form.password.data = ""
        form.repeatpassword.data = ""
    
    return render_template("register.html", form = form, username = username, email = email, password = password, repeatpassword = repeatpassword,
                           )

@app.route("/quiz_form")
def quiz_form():
    return render_template("quiz_form.html")

@app.route("/user_standings")
def user_standings():
    our_users = Users.query.order_by(Users.date_created)
    return render_template("tables.html",our_users = our_users)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")