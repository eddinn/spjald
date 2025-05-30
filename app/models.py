# app/models.py

import jwt
from datetime import datetime
from time import time
from hashlib import _hashlib

from flask import current_app
from flask_login import UserMixin
from sqlalchemy import or_

from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


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
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = _hashlib.openssl_md5(
            self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

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
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256'
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            uid = jwt.decode(
                token, current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )['reset_password']
        except Exception:
            return None
        return User.query.get(uid)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clientname = db.Column(db.String(64), index=True)
    clientss = db.Column(db.String(11), index=True, unique=True)
    clientemail = db.Column(db.String(128), index=True)
    clientphone = db.Column(db.String(24), index=True)
    clientaddress = db.Column(db.String(100), index=True)
    clientcity = db.Column(db.String(32), index=True)
    clientzip = db.Column(db.String(8), index=True)
    clientinfo = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    searchable_fields = [
        'clientname', 'clientss', 'clientemail', 'clientphone',
        'clientaddress', 'clientcity', 'clientzip', 'clientinfo'
    ]

    def __repr__(self):
        return f'<Post {self.clientname}>'

    @classmethod
    def search(cls, query, page, per_page):
        """
        Perform case-insensitive search across all searchable_fields.
        Returns a tuple (items, total).
        """
        # Build filters: field ilike %query%
        filters = [getattr(cls, field).ilike(f"%{query}%")
                   for field in cls.searchable_fields]
        q = cls.query.filter(or_(*filters)).order_by(cls.timestamp.desc())

        # Use SQLAlchemy 2-style pagination
        pagination = db.paginate(
            q,
            page=page,
            per_page=per_page,
            error_out=False
        )
        return pagination.items, pagination.total


# Flask-Login user loader
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
