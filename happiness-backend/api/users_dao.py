"""
DAO (Data Access Object) file

Helper file containing functions for accessing data in our database
"""

from models import User
from app import db


def get_user_by_username(username):
    """
    Returns a User object by username.
    :param username: Username of the User object one is searching for.
    :return: A user object that has the same username as the username that was passed in.
    """
    return User.query.filter(User.username == username).first()


def get_user_by_email(email):
    """
    Returns a user object from the database given an email
    """
    return User.query.filter(User.email == email).first()


def get_user_by_session_token(session_token):
    """
    Returns a user object from the database given a session token
    """
    return User.query.filter(User.session_token == session_token).first()


def get_user_by_update_token(update_token):
    """
    Returns a user object from the database given an update token
    """
    return User.query.filter(User.update_token == update_token).first()


def verify_credentials(email, password):
    """
    Returns true if the credentials match, otherwise returns false
    """
    optional_user = get_user_by_email(email)

    if optional_user is None:
        return False, None

    return optional_user.verify_password(password), optional_user


def renew_session(update_token):
    """
    Renews a user's session token

    Returns the User object
    """
    optional_user = get_user_by_update_token(update_token)
    if optional_user is None:
        return False, None

    optional_user.renew_session()
    db.session.commit()
    return True, optional_user
