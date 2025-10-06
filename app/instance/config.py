
import os

# Get the app directory (parent of instance)
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
db_path = os.path.join(basedir, 'app.db')

SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-Limiter settings
RATELIMIT_STORAGE_URL = "memory://"