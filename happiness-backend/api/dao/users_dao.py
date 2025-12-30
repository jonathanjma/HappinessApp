"""
DAO (Data Access Object) file

Helper file containing functions for accessing data in our database
"""
from datetime import datetime
from typing import List

from sqlalchemy import select, func

from api.app import db
from api.models.models import User, Token, Happiness


def get_user_by_id(user_id: int) -> User:
    """
    Returns a User object by ID.
    """
    return db.session.execute(select(User).where(User.id == user_id)).scalar()


def get_user_by_username(username: str) -> User:
    """
    Returns a User object by username (not case-sensitive).
    :param username: Username of the User object one is searching for.
    :return: A user object that has the same username as the username that was passed in.
    """
    return db.session.execute(select(User).where(User.username.ilike(username))).scalar()


def get_user_by_email(email: str) -> User:
    """
    Returns a user object from the database given an email with case-insensitive string comparison
    :param email: Email fo the User object one is searching for
    :return: A user object that has the same case-insensitive email, or None if the user is not found.
    """
    return db.session.execute(select(User).where(User.email.ilike(email))).scalar()


def get_token(token: str) -> Token:
    """
    Return a user object from the database given a session token
    """
    return db.session.execute(select(Token).where(Token.session_token == token)).scalar()

def get_active_users() -> List[User]:
    """
    Returns a list of users with >= 20 happiness entries since 1/1/2025 in descending order
    """
    start_date = datetime(2025, 1, 1)
    active_users = (
        db.session.query(User)
        .join(Happiness)
        .filter(Happiness.timestamp >= start_date)
        .group_by(User.id)
        .having(func.count(Happiness.id) >= 20)
        .order_by(func.count(Happiness.id).desc())
        .all()
    )
    return active_users