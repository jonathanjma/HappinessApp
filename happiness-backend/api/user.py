import datetime

import marshmallow.fields
from apifairy import authenticate, response, body, other_responses
from flask import Blueprint
from flask import json, request

from api import users_dao
from api import email_methods
from api.app import db
from api.models import User, Setting
from api.responses import success_response, failure_response
from api.schema import GroupSchema, UserSchema, CreateGroupSchema, CreateUserSchema, SettingsSchema, SettingInfoSchema
from api.token import token_auth, verify_token

import threading

user = Blueprint('user', __name__)


@user.post('/')
@body(CreateUserSchema)
@response(UserSchema, 201)
@other_responses({400: "Provided data already exists."})
def create_user(req):
    """
    Create User
    Registers a new user given an email, username, and password \n
    Requires: email and username are unique
    Returns: a JSON representation of a User object
    """
    email, username, password = req.get(
        "email"), req.get("username"), req.get("password")

    similar_user = users_dao.get_user_by_email(email)
    if similar_user is not None:
        print("ISSUE #2")
        return failure_response("Provided data already exists.", 400)
    similar_user = users_dao.get_user_by_username(username)
    if similar_user is not None:
        print("ISSUE")
        return failure_response("Provided data already exists.", 400)
    current_user = User(email=email, password=password, username=username)
    db.session.add(current_user)
    db.session.commit()

    return current_user


@user.get('/<int:user_id>')
@authenticate(token_auth)
@response(UserSchema, 200)
@other_responses({404: "Friend not found", 401: "Unauthorized: you do not share a group with this user"})
def get_user_by_id(user_id):
    """
    Get by ID
    This method gets user information from a user by querying the user by id. \n
    The req json should have "id": <int: id> passed in. \n
    Returns: JSON of User object containing user information
    """
    current_user = token_auth.current_user()

    friend_user = users_dao.get_user_by_id(user_id)
    if friend_user is None:
        return failure_response("Friend not found")
    if not current_user.has_mutual_group(friend_user):
        return failure_response("Unauthorized: you do not share a group with this user", 401)

    return friend_user


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


@user.post('/settings/')
@authenticate(token_auth)
@body(SettingInfoSchema)
@response(SettingsSchema, 201)
@other_responses({400: "Insufficient setting information provided", 401: "Unauthorized"})
def add_user_setting(req):
    """
    Add Settings
    Adds a setting to the current user's property bag. \n
    Returns: A JSON success response that contains the added setting, or a failure response.
    """
    current_user = token_auth.current_user()
    key, value = req.get("key"), req.get("value")
    setting = Setting(key=key, value=value, user_id=current_user.id)
    db.session.add(setting)
    db.session.commit()

    return setting


@user.get('/settings/')
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
        "settings": [s.serialize() for s in settings]
    })


@user.post('/username/')
@token_auth.login_required()
def change_username():
    """
    Changes a user's username to their newly desired username sent in request req.
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


@user.route('/reset_password/<token>', methods=['GET', 'POST'])
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
        return success_response({
            "reset": "Reset your password here."
        })
        pass


@user.post('/initiate_password_reset/')
def send_reset_password_email():
    """
    Sends a password reset request email to email sent in the req of the JSON request.
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


@authenticate(token_auth)
@user.post('/self/')
def get_self():
    """
    Returns a response in the form of {
        "user": <user or null>
    }
    Depending on whether the session token is valid.
    If the token_auth is invalid it returns a failure response.
    """
    return success_response({"user": token_auth.current_user()})
