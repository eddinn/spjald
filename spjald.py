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
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Spjald': Spjald}


# Database models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Spjald(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clientname = db.Column(db.String(64), index=True)
    clientemail = db.Column(db.String(128), index=True, unique=True)
    clientphone = db.Column(db.String(24), index=True)
    clientaddress = db.Column(db.String(100), index=True)
    clientcity = db.Column(db.String(32), index=True)
    clientzip = db.Column(db.String(8), index=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<clientname {}>'.format(self.clientname)
    # def __repr__(self):
    #    return '<clientname {}><clientemail {}><clientphone {}>\
    #        <clientaddress {}><clientzip {}><clientcity {}>'.format(
    #            self.clientname, self.clientemail, self.clientphone,
    #            self.clientaddress, self.clientzip, self.clientcity
    #        )


# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


# Routes
@app.route('/')
@app.route('/index')
@login_required
def index():
    spjald = {
        'client': {
            'clientname': 'Edvin Dunaway',
            'clientemail': 'edvin@eddinn.net',
            'clientphone': '+354 8581981',
            'clientaddress': 'Hlíðargata 18D',
            'clientzip': '245',
            'clientcity': 'Suðurnesjabær'
        }
    }
    return render_template('index.html', title='Home', spjald=spjald)


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
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
