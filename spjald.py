# file: spjald.py
from app import create_app, db
from app.models import User, Post

# This runs exactly once, at import time
app = create_app()

# Shell context for `flask shell`
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}