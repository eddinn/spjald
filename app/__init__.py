import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mailman import Mail
from flask_moment import Moment

# ---- GLOBAL LOGGING SETUP ----
LOG_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, 'spjald.log'),
    maxBytes=10240,
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[file_handler, console_handler]
)
logging.info("Global logging is set up at app startup.")

db = SQLAlchemy()
migrate = Migrate()
loginm = LoginManager()
loginm.login_view = 'auth.login'
loginm.login_message = ('Please log in to access this page.')
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()

def create_app(config_class=Config):
    """Flask application factory. Sets up extensions, logging, blueprints, and app context."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    loginm.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    # Register blueprints (ensure each exposes `bp`)
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # Log startup with Flask's app.logger
    app.logger.info('Spjald startup (Flask app logger)')

    # Warn if running in production with default secret key
    if (not app.config.get("SECRET_KEY") or
            app.config.get("SECRET_KEY") == "you-willnever-guess-the-supersecret-key"):
        app.logger.warning("SECRET_KEY is not set or using the default! Set a secure SECRET_KEY in production.")

    # Shell context processor for Flask CLI
    @app.shell_context_processor
    def make_shell_context():
        from app.models import User, Post
        return {'db': db, 'User': User, 'Post': Post}

    return app

# Import models to ensure they are registered with SQLAlchemy (avoid circular imports)
from app import models