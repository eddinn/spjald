import os
import logging
from flask import Flask, render_template, flash, redirect, url_for
from flask import request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin, LoginManager, current_user
from flask_login import login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from wtforms.validators import Optional, Length
from hashlib import md5
from logging.handlers import SMTPHandler, RotatingFileHandler
from datetime import datetime


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
loginm = LoginManager(app)
loginm.login_view = 'login'


@loginm.user_loader
def load_user(id):  # pylint: disable=redefined-builtin
    return User.query.get(int(id))


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Spjald': Spjald}


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


# Loggin and admin email
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/spjald.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Spjald startup')


# Database models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    spjold = db.relationship('Spjald', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def own_spjold(self):
        own = Spjald.query.filter_by(user_id=self.id)
        return own.order_by(Spjald.timestamp.desc())


class Spjald(db.Model):
    clientid = db.Column(db.Integer, primary_key=True)
    clientname = db.Column(db.String(64), index=True)
    clientss = db.Column(db.String(11), index=True, unique=True)
    clientemail = db.Column(db.String(128), index=True, unique=True)
    clientphone = db.Column(db.String(24), index=True)
    clientaddress = db.Column(db.String(100), index=True)
    clientcity = db.Column(db.String(32), index=True)
    clientzip = db.Column(db.String(8), index=True)
    clientinfo = db.Column(db.Text, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

#    def __repr__(self):
#        return '<Spjald {}>'.format(self.clientname, self.clientemail,
#                                    self.clientphone, self.clientaddress,
#                                    self.clientzip, self.clientcity)
    def __repr__(self):
        return '<Spjald {}>'.format(self.clientname)


# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    @staticmethod
    def validate_username(form, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    @staticmethod
    def validate_email(form, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class addSpjaldForm(FlaskForm):
    clientname = StringField('Name', validators=[DataRequired()])
    clientss = StringField('Social Security number', validators=[Optional()])
    clientemail = StringField('Email', validators=[DataRequired()])
    clientphone = StringField('Phone', validators=[DataRequired()])
    clientaddress = StringField('Address', validators=[Optional()])
    clientzip = StringField('ZIP', validators=[Optional()])
    clientcity = StringField('City', validators=[Optional()])
    clientinfo = TextAreaField('Info', validators=[
        Optional(), Length(min=0, max=2048)])
    submit = SubmitField('Submit')


# Routes
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = addSpjaldForm()
    if form.validate_on_submit():
        addspjald = Spjald(clientname=form.clientname.data,
                           clientss=form.clientss.data,
                           clientemail=form.clientemail.data,
                           clientphone=form.clientphone.data,
                           clientaddress=form.clientaddress.data,
                           clientzip=form.clientzip.data,
                           clientcity=form.clientcity.data,
                           clientinfo=form.clientinfo.data,
                           author=current_user)
        db.session.add(addspjald)
        db.session.commit()
        flash('Client data sucsessfully added!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    spjold = current_user.own_spjold().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=spjold.next_num) \
        if spjold.has_next else None
    prev_url = url_for('index', page=spjold.prev_num) \
        if spjold.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           spjold=spjold.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, username=form.username.data,
                    email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    spjold = Spjald.query.order_by(Spjald.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=spjold.next_num) \
        if spjold.has_next else None
    prev_url = url_for('user', username=user.username, page=spjold.prev_num) \
        if spjold.has_prev else None
    return render_template('user.html', user=user, spjold=spjold.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/search')
@login_required
def search():
    page = request.args.get('page', 1, type=int)
    spjold = Spjald.query.order_by(Spjald.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('search', page=spjold.next_num) \
        if spjold.has_next else None
    prev_url = url_for('search', page=spjold.prev_num) \
        if spjold.has_prev else None
    return render_template('index.html', title='Search', spjold=spjold.items,
                           next_url=next_url, prev_url=prev_url)
