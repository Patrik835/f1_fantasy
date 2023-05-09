from flask import Flask, render_template

# Create an instance of Flask
app = Flask(__name__)

#create route that renders index.html template
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")