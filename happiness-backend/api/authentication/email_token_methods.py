from time import time

from flask import current_app
import jwt

def generate_jwt(payload, expiration):
    """Generate a JWT with a JSON payload and an expiration time in minutes"""
    payload['exp'] = time() + expiration * 60
    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def generate_confirmation_token(email, expiration=10):
    generate_jwt({'reset_email': email}, expiration)


def confirm_email_token(token):
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_email']
    except jwt.PyJWTError:
        return
