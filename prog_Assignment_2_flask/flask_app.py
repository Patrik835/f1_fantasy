from flask import Flask, render_template, send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, AnyOf
# Create an instance of Flask
app = Flask(__name__, template_folder='templates', static_folder='static')


app.config['SECRET_KEY'] = "Thisisasecretkey"

class LoginForm(FlaskForm):
    username = StringField("select your username", validators=[InputRequired(), Length(min=3, max=15)])
    password = PasswordField("select your password", validators=[InputRequired(), Length(min=4, max=50)])
    submit = SubmitField("Login")


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
    return render_template("login.html", username = username, password = password, form = form)

@app.route("/quiz_form")
def quiz_form():
    return render_template("quiz_form.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")