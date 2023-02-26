from apifairy import authenticate, response
from flask import Blueprint
from flask import json, request

from api import users_dao
from api import email_methods
from api.app import db
from api.models import User, Setting
from api.responses import success_response, failure_response
from api.schema import GroupSchema
from api.token import token_auth

import threading

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

    return success_response({"user": current_user.serialize()}, 201)


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


@user.post('/username/')
@token_auth.login_required()
def change_username():
    """
    Changes a user's username to their newly desired username sent in request body.
    Requires json to be passed with username as the key.
    """
    body = json.loads(request.data)
    new_username = body.get("username")
    current_user = token_auth.current_user()
    if new_username is None:
        return failure_response("New username not provided", 400)
    current_user.username = new_username
    db.session.commit()
    return success_response({
        "username": current_user.username
    })


@user.route('/reset_password/<token>/', methods=['GET', 'POST'])
def reset_password(token):
    """
    IMPORTANT:
    This function was written under the assumption that when the user receives a verify password email,
    they would be redirected to a page where they are prompted to enter a new password. Then from this page they
    make a post request to the backend with their new intended password. For a get request, the route currently
    shows a basic success response. This will be replaced with the front-end page to reset your password.

    This route is not included in testing as it is very difficult to automate since it uses emails. However it has
    been tested using Postman and should work properly.
    """
    if request.method == "POST":
        # Reset password to desired password
        current_user = User.verify_reset_password(token)
        if not current_user:
            return failure_response("Password reset token verification failed, token may be expired")

        body = json.loads(request.data)
        pwd = body.get("password")
        if pwd is None:
            return failure_response("New password not provided", 401)
        else:
            current_user.set_password(pwd)
            db.session.commit()
            return success_response({
                "user": current_user.serialize(),
                "password hash": str(current_user.password_digest)
            })
    else:
        # Display password reset page, this allows user to post new password to this request.
        # TODO this is a placeholder and we will need to route this to show something on the frontend.
        return success_response({
            "reset": "Reset your password here."
        })
        pass


@user.post('/initiate_password_reset/')
def send_reset_password_email():
    """
    Sends a password reset request email to email sent in the body of the JSON request.
    :return: a success response or failure response depending on the result of the operation
    """
    body = json.loads(request.data)
    email = body.get("email")
    if email is None:
        return failure_response("Need an email to send password reset link.", 400)
    user_by_email = users_dao.get_user_by_email(email)
    if user_by_email is None:
        return failure_response("User associated email not found")
    threading.Thread(target=email_methods.send_password_reset_email, args=(user_by_email,)).start()
    return success_response({
        "user": user_by_email.serialize()
    })
