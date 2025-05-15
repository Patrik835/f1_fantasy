from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from config import Config

# Create an instance of Flask
app = Flask(__name__)
app.config.from_object(Config)

# Initialize CSRF protection
csrf = CSRFProtect()
csrf.init_app(app)

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

with app.app_context():
    from flask_app import routes
    db.create_all()

    # Create default roles if they don't exist
    from flask_app.models import Role
    if not Role.query.filter_by(name='admin').first():
        admin_role = Role(name='admin')
        db.session.add(admin_role)
    if not Role.query.filter_by(name='user').first():
        user_role = Role(name='user')
        db.session.add(user_role)
    db.session.commit()

def create_app():
    return app