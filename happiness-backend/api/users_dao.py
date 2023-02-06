"""
DAO (Data Access Object) file

Helper file containing functions for accessing data in our database
"""

from api.models import User, Group


def get_user_by_id(id):
    return User.query.filter(User.id == id).first()


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


def get_group_by_id(group_id):
    return Group.query.filter(Group.id == group_id).first()
