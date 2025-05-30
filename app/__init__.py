import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'

# Tell Flask-Login how to load a user from the session
from app.models import User

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    # Register blueprints, ignoring duplicates
    from app.errors import bp as errors_bp
    try:
        app.register_blueprint(errors_bp)
    except AssertionError:
        pass

    from app.auth import bp as auth_bp
    try:
        app.register_blueprint(auth_bp)
    except AssertionError:
        pass

    from app.main import bp as main_bp
    try:
        app.register_blueprint(main_bp)
    except AssertionError:
        pass

    # Production logging setup
    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'):
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = () if app.config.get('MAIL_USE_TLS') else None
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=f"no-reply@{app.config['MAIL_SERVER']}",
                toaddrs=app.config['ADMINS'], subject='Spjald Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/spjald.log',
                                           maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Spjald startup')

    return app

from app import models
