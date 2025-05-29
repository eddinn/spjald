from flask_mailman import EmailMessage
from app import mail
from flask import current_app
from threading import Thread

def send_async_email(app, msg):
    """Send email message in a separate thread within the app context."""
    with app.app_context():
        msg.send()

def send_email(subject, sender, recipients, text_body, html_body):
    """
    Compose and send an email asynchronously.

    Args:
        subject (str): Email subject.
        sender (str): Sender's email address.
        recipients (list): List of recipient email addresses.
        text_body (str): Plain text email body.
        html_body (str): HTML email body.
    """
    msg = EmailMessage(
        subject=subject,
        body=text_body,
        from_email=sender,
        to=recipients
    )
    msg.content_subtype = "plain"  # Main content is plain text
    msg.body = text_body
    if html_body:
        msg.alternatives = [(html_body, "text/html")]
    # Start sending in background
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg), daemon=True).start()