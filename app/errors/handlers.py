# app/errors/handlers.py

from flask import render_template, current_app
from app import db
from app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    # Log a warning for 404s
    current_app.logger.warning(f'404 Not Found: {error}', exc_info=False)
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    # Log the full stack trace for 500s
    current_app.logger.error(f'500 Internal Server Error: {error}', exc_info=True)
    # Roll back any failed database transaction
    db.session.rollback()
    return render_template('errors/500.html'), 500