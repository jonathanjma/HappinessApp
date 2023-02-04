from flask_mail import Message

from api import create_app
from api.app import mail

app = create_app()


def send_verify_email_async(email):
    with app.app_context():
        msg = Message("Hello world!", sender="noreply@happinessapp.org", recipients=[email])
        msg.body = "Verify your email here."
        mail.send(msg)
