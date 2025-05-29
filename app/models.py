from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, loginm


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def followed_posts(self):
        return Post.query.filter_by(author_id=self.id).order_by(Post.timestamp.desc())


@loginm.user_loader
def load_user(id):
    return db.session.get(User, int(id))  # SQLAlchemy 2.0+ pattern


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clientname = db.Column(db.String(128))
    clientss = db.Column(db.String(32), unique=True)
    clientemail = db.Column(db.String(128), unique=True)
    clientphone = db.Column(db.String(32))
    clientaddress = db.Column(db.String(256))
    clientzip = db.Column(db.String(16))
    clientcity = db.Column(db.String(64))
    clientinfo = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
