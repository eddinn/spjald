import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-willnever-guess-the-supersecret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    DEBUG = False
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '25'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = [x.strip() for x in os.environ.get('ADMINS', '').split(',') if x]
    POSTS_PER_PAGE = int(os.environ.get('POSTS_PER_PAGE', 10))
    # Add any other config settings as needed

    @staticmethod
    def validate_config():
        if Config.SECRET_KEY == 'you-willnever-guess-the-supersecret-key':
            import warnings
            warnings.warn("Using default SECRET_KEY! Set a secure SECRET_KEY environment variable in production.", UserWarning)

Config.validate_config()