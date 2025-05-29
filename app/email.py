from flask_mailman import EmailMessage
from app import mail
from flask import current_app
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        msg.send()

def send_email(subject, sender, recipients, text_body, html_body):
    msg = EmailMessage(
        subject=subject,
        body=text_body,
        from_email=sender,
        to=recipients
    )
    msg.content_subtype = "plain"
    msg.body = text_body
    msg.alternatives = [(html_body, "text/html")]
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()