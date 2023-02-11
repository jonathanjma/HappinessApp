from apifairy import authenticate, response
from flask import Blueprint
from flask import json, request

from api import users_dao
from api.app import db
from api.models import User, Setting
from api.responses import success_response, failure_response
from api.schema import GroupSchema
from api.token import token_auth

user = Blueprint('user', __name__)


@user.post('/')
def create_user():
    """
    Create User
    Registers a new user given an email, username, and password \n
    Requires: email and username are unique
    """
    body = json.loads(request.data)
    email, username, password = body.get(
        "email"), body.get("username"), body.get("password")
    if username is None or email is None or password is None:
        return failure_response("Insufficient information", 400)

    similar_user = users_dao.get_user_by_email(email)
    if similar_user is not None:
        return failure_response("An account has already been made with this email.", 400)
    similar_user = users_dao.get_user_by_username(username)
    if similar_user is not None:
        return failure_response("Username is already taken.", 400)
    current_user = User(email=email, password=password, username=username)
    db.session.add(current_user)
    db.session.commit()

    return '', 201


@user.get('/')
@authenticate(token_auth)
def get_user_by_id():
    """
    Get by ID
    This method gets user information from a user by querying the user by id. \n
    The body json should have "id": <int: id> passed in. \n
    Returns: JSON of User object containing user information
    """
    # TODO this method should only be allowed to be called by someone in the same group as the target user.
    body = json.loads(request.data)
    friend_id = body.get("id")
    friend_user = users_dao.get_user_by_id(friend_id)
    if friend_user is None:
        return failure_response("Friend not found")
    return success_response({
        "id": friend_id,
        "username": friend_user.username,
        "profile_picture": friend_user.profile_picture,
        "settings": [s.serialize() for s in friend_user.settings],
    })


@user.get('/groups')
@authenticate(token_auth)
@response(GroupSchema(many=True))
def user_groups():
    """
    Get Groups
    Gets the happiness groups the user is in. \n
    Returns: a list of happiness groups that the user is in.
    """
    return token_auth.current_user().groups


@user.delete('/')
@authenticate(token_auth)
def delete_user():
    """
    Delete User
    Deletes the user that is currently logged in, including all user data. \n
    Returns: A success with serialized user or failure response with the appropriate message.
    """
    current_user = token_auth.current_user()
    db.session.delete(current_user)
    db.session.commit()

    return success_response(current_user.serialize(), 200)


@user.post('/settings')
@authenticate(token_auth)
def add_user_setting():
    """
    Add Settings
    Adds a setting to the current user's property bag. \n
    Returns: A JSON success response that contains the added setting, or a failure response.
    """
    body = json.loads(request.data)
    current_user = token_auth.current_user()
    key, value = body.get("key"), body.get("value")
    if key is None or value is None:
        return failure_response("Insufficient setting information provided", 400)
    setting = Setting(key=key, value=value, user_id=current_user.id)
    db.session.add(setting)
    db.session.commit()

    return success_response(setting.serialize(), 201)


@user.get('/settings')
@authenticate(token_auth)
def get_user_settings():
    """
    Get Settings
    Gets the settings of the current user by authorization token. \n
    Returns: A JSON response of a list of key value pairs that contain setting keys and their values for the user.
    """
    current_user = token_auth.current_user()
    settings = Setting.query.filter(Setting.user_id == current_user.id).all()
    return success_response({
        "settings": [(s.key, s.value) for s in settings]
    })
