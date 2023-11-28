"""
DAO (Data Access Object) file

Helper file containing functions for accessing data in our database
"""
from sqlalchemy import select

from api.app import db
from api.models.models import User, Token


def get_user_by_id(user_id: int) -> User:
    """
    Returns a User object by ID.
    """
    return db.session.execute(select(User).where(User.id == user_id)).scalar()


def get_user_by_username(username):
    """
    Returns a User object by username (not case-sensitive).
    :param username: Username of the User object one is searching for.
    :return: A user object that has the same username as the username that was passed in.
    """
    return User.query.filter(User.username.ilike(username)).first()


def get_user_by_email(email):
    """
    Returns a user object from the database given an email with case-insensitive string comparison
    :param email: Email fo the User object one is searching for
    :return: A user object that has the same case-insensitive email, or None if the user is not found.
    """
    return User.query.filter(User.email.ilike(email)).first()


def get_token(token: str) -> Token:
    """
    Return a user object from the database given a session token
    """
    return db.session.execute(select(Token).where(Token.session_token == token)).scalar()
