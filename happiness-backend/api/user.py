import datetime

import marshmallow.fields as ma
from apifairy import authenticate, response, body, other_responses
from flask import Blueprint
from flask import json, request

from api import users_dao
from api import email_methods
from api.app import db
from api.models import User, Setting
from api.responses import success_response, failure_response
from api.schema import GroupSchema, UserSchema, CreateGroupSchema, CreateUserSchema, SettingsSchema, SettingInfoSchema, \
    UsernameSchema, UserEmailSchema, ManySettingsSchema
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
        return failure_response("Provided data already exists", 400)
    similar_user = users_dao.get_user_by_username(username)
    if similar_user is not None:
        return failure_response("Provide data already exists", 400)
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
    Get User by ID
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
@response(UserSchema)
@other_responses({401: "Unauthorized"})
def delete_user():
    """
    Delete User
    Deletes the user that is currently logged in, including all user data. \n
    Returns: A success with serialized user or failure response with the appropriate message.
    """
    current_user = token_auth.current_user()
    db.session.delete(current_user)
    db.session.commit()

    return current_user


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
@response(SettingsSchema(many=True))
def get_user_settings():
    """
    Get Settings
    Gets the settings of the current user by authorization token. \n
    Returns: A JSON response of a list of key value pairs that contain setting keys and their values for the user.
    """
    current_user = token_auth.current_user()
    settings = Setting.query.filter(Setting.user_id == current_user.id).all()
    return settings


@user.post('/username/')
@token_auth.login_required()
@body(UsernameSchema)
@response(UserSchema)
@other_responses({401: "Unauthorized"})
def change_username(req):
    """
    Change Username \n
    Changes a user's username to their newly desired username sent in request req. \n
    Requires json to be passed with username as the key.
    """
    new_username = req.get("username")
    current_user = token_auth.current_user()

    current_user.username = new_username
    db.session.commit()
    return current_user


@user.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Reset Password from Token
    IMPORTANT:
    This function was written under the assumption that when the user receives a verify password email, \n
    they would be redirected to a page where they are prompted to enter a new password. Then from this page they \n
    make a post request to the backend with their new intended password. For a get request, the route currently \n
    shows a basic success response. This will be replaced with the front-end page to reset your password. \n \n

    This route is not included in testing as it is very difficult to automate since it uses emails. \n
    However, it has been tested using Postman and should work properly.
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
                "password hash": str(current_user.password)
            })
    else:
        # Display password reset page, this allows user to post new password to this request.
        return success_response({
            "reset": "Reset your password here."
        })
        pass


@user.post('/initiate_password_reset/')
@body(UserEmailSchema)
@response(UserSchema)
@other_responses({404: "User associated with email address not found"})
def send_reset_password_email(req):
    """
    Send Reset Password Email
    Sends a password reset request email to email sent in the req of the JSON request. \n
    :return: a success response or failure response depending on the result of the operation
    """
    email = req.get("email")
    user_by_email = users_dao.get_user_by_email(email)
    if user_by_email is None:
        return failure_response("User associated with email address not found")
    threading.Thread(target=email_methods.send_password_reset_email, args=(user_by_email,)).start()
    return user_by_email


@authenticate(token_auth)
@user.post('/self/')
@response(UserSchema)
@other_responses({401: "Unauthorized"})
def get_self():
    """
    Get Self
    Returns the user object depending on whether the session token is valid. \n
    If the token_auth is invalid it returns a failure response.
    """
    return token_auth.current_user()
