from flask import current_app
from api.app import mail
from flask_mail import Message
from flask import render_template


def send_email_helper(subject, sender, recipients, text_body, html_body):
    """
    Helper method to send emails using Flask-Mail
    :param subject: Subject line of email.
    :param sender: Email address to send the email.
    :param recipients: Recipients of the email.
    :param text_body: Rendered template of email req text.
    :param html_body: Rendered template of html email req.
    """
    with current_app._get_current_object().app_context:  # magic
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        mail.send(msg)


def send_password_reset_email(user):
    """
    Sends a password reset email to specified user.
    :param user: The user to send the password reset email to.
    """
    with current_app._get_current_object().app_context():  # magic
        token = user.get_reset_password_token()
        send_email_helper('Happiness App Password Reset',
                          sender="noreply@happinessapp.org",
                          recipients=[user.email],
                          text_body=render_template('reset_password.txt', user=user, token=token),
                          html_body=render_template('reset_password.html', user=user, token=token))
