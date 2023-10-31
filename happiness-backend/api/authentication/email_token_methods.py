from time import time

from flask import current_app
import jwt


def generate_confirmation_token(email, expiration=10):
    return jwt.encode(
        {
            'exp': time() + expiration * 60, # expiration is in minutes
            'reset_email': email,
        },
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )


def confirm_email_token(token):
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_email']
    except jwt.PyJWTError:
        return
