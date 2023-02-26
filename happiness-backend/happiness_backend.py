from flask_mail import Message

from api import create_app
from api.app import db
from api.models import User, Setting, Happiness
from api.app import mail

app = create_app()


def send_verify_email_async(email):
    with app.app_context():
        msg = Message("Hello world!", sender="noreply@happinessapp.org", recipients=[email])
        msg.body = "Verify your email here."
        mail.send(msg)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Setting': Setting, 'Happiness': Happiness}