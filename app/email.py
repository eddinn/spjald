# app/email.py

from flask import render_template, current_app
from flask_mail import Message
from app import mail
from threading import Thread

def _send_async_email(app, msg):
    """Send the email message within the Flask app context."""
    with app.app_context():
        mail.send(msg)

def send_password_reset_email(user):
    """
    Generate a token for `user`, build a reset‐password email,
    and send it asynchronously.
    """
    # Create the token
    token = user.get_reset_password_token()

    # Build message
    subject = '[Spjald] Reset Your Password'
    sender = current_app.config['ADMINS'][0] if current_app.config.get('ADMINS') else None
    recipients = [user.email]

    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = render_template(
        'email/reset_password.txt',
        user=user, token=token
    )
    msg.html = render_template(
        'email/reset_password.html',
        user=user, token=token
    )

    # Fire-and-forget via background thread
    Thread(
        target=_send_async_email,
        args=(current_app._get_current_object(), msg)
    ).start()
