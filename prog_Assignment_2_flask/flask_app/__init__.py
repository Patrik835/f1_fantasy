from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Create an instance of Flask
app = Flask(__name__)
#add database
#sqlite db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#secret key for forms
app.config['SECRET_KEY'] = "Thisisasecretkey"

db = SQLAlchemy(app)
app.app_context().push()
migrate = Migrate(app, db)


from flask_app import routes, scraper