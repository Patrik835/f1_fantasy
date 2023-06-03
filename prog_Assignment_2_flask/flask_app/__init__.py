from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# Create an instance of Flask
app = Flask(__name__)
#add database
#sqlite db
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://sjyvtcwsyfbzri:264435dd3efa106759f3c23dc3f332fc608b9b89483bd2a57cbd7023a42a9a3d@ec2-34-202-127-5.compute-1.amazonaws.com:5432/dahqcu812ug0gr'


#secret key for forms
app.config['SECRET_KEY'] = "Thisisasecretkey"
csrf = CSRFProtect(app)

db = SQLAlchemy(app)
app.app_context().push()
migrate = Migrate(app, db)


from flask_app import routes, scraper