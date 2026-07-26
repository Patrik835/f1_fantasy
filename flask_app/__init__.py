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

@login_manager.user_loader
def load_user(user_id):
    from flask_app.models import User
    return db.session.get(User, int(user_id))


def seed_default_roles():
    from flask_app.models import Role

    if not Role.query.filter_by(name='admin').first():
        admin_role = Role(name='admin')
        db.session.add(admin_role)
    if not Role.query.filter_by(name='user').first():
        user_role = Role(name='user')
        db.session.add(user_role)
    db.session.commit()


def init_db():
    db.create_all()
    seed_default_roles()


@app.cli.command("init-db")
def init_db_command():
    init_db()
    print("Initialized database and default roles.")


def create_app():
    return app


from flask_app import routes
