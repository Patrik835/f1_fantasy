from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# Create an instance of Flask
app = Flask(__name__)
#add database
#sqlite db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#mariajaws db
# app.config['JAWSDB_MARIA_URL'] = "mysql://xl8a6x27iak68qvf:xfqm6rvfyqdcxp4i@un0jueuv2mam78uv.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/axdd4me1qphqzzxu"

#secret key for forms
app.config['SECRET_KEY'] = "Thisisasecretkey"

csrf = CSRFProtect(app)
db = SQLAlchemy(app)
app.app_context().push()
migrate = Migrate(app, db)


from flask_app import routes, scraper