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

def verify_token(token):
    """
    Verify that a JWT is valid and not expired.
    Returns the JWT payload if it is valid, otherwise returns None
    """
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.PyJWTError:
        return
