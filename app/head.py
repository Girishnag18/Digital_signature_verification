# app/head.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import warnings

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
 
db = SQLAlchemy()
login_manager = LoginManager()
# Suppress Flask-Limiter warning for development
warnings.filterwarnings("ignore", message="Using the in-memory storage for tracking rate limits")
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://"
)


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Try to load instance config, fall back to default if not found
    try:
        app.config.from_pyfile('config.py')
    except FileNotFoundError:
        # Default configuration
        db_path = os.path.join(BASE_DIR, "app.db")
        app.config.update(
            SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
            SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', f'sqlite:///{db_path}'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False
        )

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # Import and register routes blueprint
    from app.routes import bp
    if bp.name not in app.blueprints:
        app.register_blueprint(bp)
    
    # Set the login view after blueprint registration
    login_manager.login_view = 'main.login'  # assuming your login route is in the main blueprint

    # Import models and admin views AFTER app is created and db is initialized
    # so models and db.session are available.
    try:
        from flask_admin import Admin
        from flask_admin.contrib.sqla import ModelView
        from app.models import User, DocumentLog
        from app.admin import SecureModelView

        # Flask-Admin setup
        admin = Admin(app, name='Admin Dashboard', template_mode='bootstrap4')
        admin.add_view(SecureModelView(User, db.session))
        admin.add_view(SecureModelView(DocumentLog, db.session))
    except ImportError as e:
        print(f"Warning: Could not set up Flask-Admin: {e}")
    except Exception as e:
        print(f"Warning: Error setting up admin views: {e}")

    return app


# -----------------------
# Flask-Login User Loader
# -----------------------
# Define the user loader at module level so Flask-Login can call it when
# reloading the user from the session cookie.
#
# If your project uses an application factory (create_app) this module will
# be imported at startup and the loader will be available. The loader imports
# the User model lazily to avoid circular imports during initial module import.

try:
    # Try to import User at module import time (works for simple apps)
    from app.models import User  # adjust if your package name is different
except Exception:
    User = None


@login_manager.user_loader
def load_user(user_id):
    """
    Given user_id (a unicode) return the User object, or None if not found.

    Flask-Login stores the user_id in the session when the user logs in.
    This function tells Flask-Login how to reload that user from the DB.
    """
    if user_id is None:
        return None

    # Ensure we have the User class; attempt lazy import for factory apps
    if User is None:
        try:
            from app.models import User as _User
            return db.session.get(_User, int(user_id))
        except Exception:
            return None

    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None