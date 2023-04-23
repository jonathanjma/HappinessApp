from apifairy import authenticate, response, body, other_responses
from flask import Blueprint
from flask import json, request

from api import users_dao
from api import email_methods
from api.app import db
from api.email_token_methods import confirm_email_token
from api.models import User, Setting
from api.responses import success_response, failure_response
from api.schema import GroupSchema, UserSchema, CreateUserSchema, SettingsSchema, SettingInfoSchema, \
    UsernameSchema, UserEmailSchema, SimpleUserSchema
from api.token import token_auth


import threading

user = Blueprint('user', __name__)


@user.post('/')
@body(CreateUserSchema)
@response(UserSchema, 201)
@other_responses({400: "Provided data already exists."})
def create_user(req):
    """
    Create User
    Registers a new user given an email, username, and password. \n
    Requires: Email and username are unique. \n
    Returns: JSON representation of User object.
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
@response(UserSchema)
@other_responses({404: "User not found.", 403: "You do not share a group with this user."})
def get_user_by_id(user_id):
    """
    Get User by ID
    This method gets user information from a user by querying the user by id.
    User must share a group with the user they are viewing. \n
    Returns: JSON of User object containing user information
    """
    current_user = token_auth.current_user()

    friend_user = users_dao.get_user_by_id(user_id)
    if friend_user is None:
        return failure_response("User not found", 404)
    if not current_user.has_mutual_group(friend_user):
        return failure_response("Not Allowed: you do not share a group with this user", 403)

    return friend_user

@user.get('/username/<username>')
@authenticate(token_auth)
@response(SimpleUserSchema)
@other_responses({404: "User not found"})
def get_user_by_username(username):
    """
    Get User by Username
    Returns the basic information (id, username, profile picture) about a user by querying by username.
    Returns 404 if no such user exists.
    """
    user_lookup = users_dao.get_user_by_username(username)
    if user_lookup is None:
        return failure_response("User not found", 404)
    return user_lookup

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
def delete_user():
    """
    Delete User
    Deletes the user that is currently logged in, including all user data.
    """
    current_user = token_auth.current_user()
    db.session.delete(current_user)
    db.session.commit()

    return '', 204


@user.post('/settings/')
@authenticate(token_auth)
@body(SettingInfoSchema)
@response(SettingsSchema, 201)
@other_responses({400: "Insufficient information provided."})
def add_user_setting(req):
    """
    Add Settings
    Adds a setting to the current user's property bag. \n
    If the setting already exists in the property bag, it modifies the value of the setting. \n
    Returns: A JSON success response that contains the added setting, or a failure response.
    """
    current_user = token_auth.current_user()
    key, value = req.get("key"), req.get("value")
    oldSetting = Setting.query.filter(Setting.user_id == current_user.id, Setting.key == key).first()
    if oldSetting is None:
        print("OLD SETTING NOT FOUND -----------------")
        newSetting = Setting(key=key, value=value, user_id=current_user.id)
        db.session.add(newSetting)
        db.session.commit()
        return newSetting

    oldSetting.value = value
    db.session.commit()
    print("Old setting updated")
    return oldSetting


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
@authenticate(token_auth)
@body(UsernameSchema)
@response(UserSchema)
@other_responses({400: "Provided data already exists."})
def change_username(req):
    """
    Change Username \n
    Changes a user's username to their newly desired username \n
    Requires: Username is unique.
    """
    new_username = req.get("username")
    current_user = token_auth.current_user()

    similar_user = users_dao.get_user_by_username(new_username)
    if similar_user is not None:
        return failure_response("Provide data already exists", 400)

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
        current_user = users_dao.get_user_by_email(confirm_email_token(token))
        if not current_user:
            return failure_response("Password reset token verification failed, token may be expired", 401)

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
    Returns: a success response or failure response depending on the result of the operation
    """
    email = req.get("email")
    user_by_email = users_dao.get_user_by_email(email)
    if user_by_email is None:
        return failure_response("User associated with email address not found", 400)
    threading.Thread(target=email_methods.send_password_reset_email, args=(user_by_email,)).start()
    return user_by_email


@user.get('/self/')
@authenticate(token_auth)
@response(UserSchema)
def get_self():
    """
    Get Self
    Returns: the user object corresponding to the currently logged in user.
    """
    return token_auth.current_user()
