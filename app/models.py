from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, loginm

class User(UserMixin, db.Model):
    """User model for authentication and user management."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the user's password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        """Generates a password reset token for this user."""
        from itsdangerous import URLSafeTimedSerializer
        from flask import current_app
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_password_token(token, max_age=600):
        """Verifies a password reset token and returns the user if valid."""
        from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
        from flask import current_app
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=max_age)
        except (BadSignature, SignatureExpired):
            return None
        user_id = data.get('user_id')
        if user_id is None:
            return None
        return db.session.get(User, user_id)

    def followed_posts(self):
        """Returns this user's posts, ordered by most recent."""
        return Post.query.filter_by(author_id=self.id).order_by(Post.timestamp.desc())

    def __repr__(self):
        return f'<User {self.username}>'

@loginm.user_loader
def load_user(user_id):
    """Flask-Login user loader callback."""
    return db.session.get(User, int(user_id))  # SQLAlchemy 2.0+ pattern

class Post(db.Model):
    """Post model, represents a client or post made by a user."""
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

    def __repr__(self):
        return f'<Post {self.clientname} ({self.clientemail})>'