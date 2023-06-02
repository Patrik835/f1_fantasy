from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# Create an instance of Flask
app = Flask(__name__)
#add database
#sqlite db
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://luskdaihpcphpe:810b682365bcacc2ad7cf06fc6b5c1a5ec23554e06856c1cb697c75451921655@ec2-34-197-91-131.compute-1.amazonaws.com:5432/d3v3eph8tuc1hr'


#secret key for forms
app.config['SECRET_KEY'] = "Thisisasecretkey"
csrf = CSRFProtect(app)

db = SQLAlchemy(app)
app.app_context().push()
migrate = Migrate(app, db)


from flask_app import routes, scraper