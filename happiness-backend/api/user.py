import datetime

from flask import Blueprint
from api.models import User, Setting
from api.responses import success_response, failure_response
from flask import json, request
from api.app import db
from api import users_dao

user = Blueprint('user', __name__)


def extract_token(my_request):
    """
    Helper function that extracts the token from the header of a request
    """
    auth_header = my_request.headers.get("Authorization")
    if auth_header is None:
        return False, failure_response("Missing authorization header", 400)

    # Header looks like "Authorization: Bearer <token>"
    bearer_token = auth_header.replace("Bearer ", "").strip()
    if bearer_token is None or not bearer_token:
        return False, failure_response("Invalid authorization header", 400)

    return True, bearer_token


@user.post('/')
def create_user():
    body = json.loads(request.data)
    email, username, password = body.get("email"), body.get("username"), body.get("password")
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

    return success_response({
        "session_token": current_user.session_token,
        "session_expiration": str(current_user.session_expiration),
        "update_token": current_user.update_token,
    }, 201)


@user.post('/settings/')
def add_user_setting():
    """
    Adds a setting to the current user's property bag.
    :return: A JSON success response that contains the added setting, or a failure response.
    """
    body = json.loads(request.data)
    success, token = extract_token(request)
    if not success:
        return failure_response("Session token not found. Relog?")
    current_user = users_dao.get_user_by_session_token(token)
    if current_user is None or not current_user.verify_session_token(token):
        return failure_response("Current user not found. Relog?")
    key, value = body.get("key"), body.get("value")
    if key is None or value is None:
        return failure_response("Insufficient setting information provided", 400)
    setting = Setting(key=key, value=value, user_id=current_user.id)
    db.session.add(setting)
    db.session.commit()

    return success_response(setting.serialize(), 201)


@user.get('/settings/')
def get_user_settings():
    """
    Gets the settings of the current user by authorization token.
    :return: A JSON response of a list of key value pairs that contain setting keys and their values for the user.
    """
    success, token = extract_token(request)
    if not success:
        return failure_response("Session token not found. Relog?")
    current_user = users_dao.get_user_by_session_token(token)
    if current_user is None or not current_user.verify_session_token(token):
        return failure_response("User with current session token not found. Relog?")
    settings = Setting.query.filter(Setting.user_id == current_user.id).all()
    return success_response({
        "settings": [(s.key, s.value) for s in settings]
    })


@user.get('/')
def get_user_by_id():
    """
    This method gets user information from a user by querying the user by id.
    The body json should have "id": <int: id> passed in.
    TODO this method should only be allowed to be called by someone in the same group as the target user.
    :return: JSON of User object containing user information
    """
    success, token = extract_token(request)
    if not success or token is None:
        return failure_response("You need to be logged in to perform this action", 401)
    current_user = users_dao.get_user_by_session_token(token)
    if current_user is None or not current_user.verify_session_token(token):
        return failure_response("You need to be logged in to perform this action", 401)

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


@user.post('/logout/')
def logout_user():
    """
    Logs out the current user.
    :return: a success or failure response based on whether we were able to log out the user.
    """
    success, token = extract_token(request)
    if not success or token is None:
        return failure_response("User not found")
    current_user = users_dao.get_user_by_session_token(token)
    if current_user is None:
        return failure_response("User not found")

    current_user.session_token = ""
    current_user.session_expiration = datetime.datetime.now()
    current_user.update_token = ""
    db.session.commit()

    return success_response({"message": "You have successfully logged out"})


@user.post('/login/')
def login_user():
    body = json.loads(request.data)
    email, password = body.get("email"), body.get("password")
    if email is None or password is None:
        return failure_response("Provide all login credentials", 400)
    success, current_user = users_dao.verify_credentials(email, password)

    if not success:
        return failure_response("Incorrect login credentials", 401)

    if current_user is None:
        return failure_response("User not found", 404)

    if datetime.datetime.now() > current_user.session_expiration:
        print("hello")
        current_user.renew_session()
        db.session.commit()

    return success_response({
        "session_token": current_user.session_token,
        "session_expiration": str(current_user.session_expiration),
        "update_token": current_user.update_token,
    })


@user.delete('/')
def delete_user():
    """
    Deletes the user that is currently logged in, including all user data.
    :return: A success with serialized user or failure response with the appropriate message.
    """
    success, token = extract_token(request)
    if not success:
        return failure_response("You must be logged in to perform this action", 401)
    current_user = users_dao.get_user_by_session_token(token)
    if current_user is None or not current_user.verify_session_token(token):
        return failure_response("Your account was not found.", 404)

    db.session.delete(current_user)
    db.session.commit()
    return success_response(current_user.serialize(), 200)
