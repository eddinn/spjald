import jwt
from datetime import datetime
from app import app, db, loginm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import _hashlib
from time import time


@loginm.user_loader
def load_user(id):  # pylint: disable=redefined-builtin
    return User.query.get(int(id))


# Database models
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer,
                               db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer,
                               db.ForeignKey('user.id')))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = _hashlib.openssl_md5(
            self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(  # pylint: disable=redefined-builtin
                token, app.config['SECRET_KEY'],
                algorithms=['HS256'])['reset_password']
        except Exception as e:
            print("EXCEPTION FORMAT PRINT:\n{}".format(e))
            return
        return User.query.get(id)


class Post(db.Model):
    clientid = db.Column(db.Integer, primary_key=True)
    clientname = db.Column(db.String(64), index=True)
    clientss = db.Column(db.String(11), index=True, unique=True)
    clientemail = db.Column(db.String(128), index=True, unique=True)
    clientphone = db.Column(db.String(24), index=True)
    clientaddress = db.Column(db.String(100), index=True)
    clientcity = db.Column(db.String(32), index=True)
    clientzip = db.Column(db.String(8), index=True)
    clientinfo = db.Column(db.Text, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # def __repr__(self):
    #    return '{}'.format(self.clientname, self.clientss,
    #                       self.clientemail, self.clientphone,
    #                       self.clientaddress, self.clientcity,
    #                       self.clientzip, self.clientinfo)
    def __repr__(self):
        return '{}'.format(self.clientname)
