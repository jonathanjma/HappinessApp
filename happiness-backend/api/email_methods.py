from flask_mail import Message, Mail
from flask import render_template

global my_app
global mail


def init_app(app):
    global my_app
    global mail
    mail = Mail()
    my_app = app
    mail.init_app(my_app)


def send_email_helper(subject, sender, recipients, text_body, html_body):
    """
    Helper method to send emails using Flask-Mail
    :param subject: Subject line of email.
    :param sender: Email address to send the email.
    :param recipients: Recipients of the email.
    :param text_body: Rendered template of email req text.
    :param html_body: Rendered template of html email req.
    """
    with my_app.app_context():  # magic
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        mail.send(msg)


def send_password_reset_email(user):
    """
    Sends a password reset email to specified user.
    :param user: The user to send the password reset email to.
    """
    # TODO fix authentication for email account, get happiness email for domain?
    with my_app.app_context():
        token = user._urlsafe_base_64()
        send_email_helper('Happiness App Password Reset',
                          sender="noreply@happinessapp.org",
                          recipients=[user.email],
                          text_body=render_template('reset_password.txt', user=user, token=token),
                          html_body=render_template('reset_password.html', user=user, token=token))
