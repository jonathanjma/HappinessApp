from apifairy import authenticate, response, body, other_responses
from flask import Blueprint

from api.dao import users_dao
from api import email_methods
from api.app import db
from api.dao.groups_dao import get_group_by_id
from api.email_token_methods import confirm_email_token
from api.models import User, Setting
from api.errors import failure_response
from api.schema import UserSchema, CreateUserSchema, SettingsSchema, SettingInfoSchema, \
    UsernameSchema, PasswordResetReqSchema, SimpleUserSchema, EmptySchema, PasswordResetSchema, \
    UserGroupsSchema
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
    similar_user2 = users_dao.get_user_by_username(username)
    if similar_user2 is not None:
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
    if friend_user.id != current_user.id and not current_user.has_mutual_group(friend_user):
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
@response(UserGroupsSchema)
def user_groups():
    """
    Get Groups
    Returns: a list of happiness groups that the user is in as well as any they have been invited to join.
    """
    return {
        'groups': token_auth.current_user().groups,
        'group_invites': token_auth.current_user().invites
    }


@user.post('/accept_invite/<int:group_id>')
@authenticate(token_auth)
@response(EmptySchema, 204, 'Group invite accepted')
@other_responses({404: 'Invalid Group Invite'})
def accept_group_invite(group_id):
    """
    Accept Group Invite
    Accepts an invite to join a happiness group \n
    Requires: group ID is valid and corresponds to a group that has invited the user
    """
    group = get_group_by_id(group_id)
    if group is not None and group in token_auth.current_user().invites:
        group.add_user(token_auth.current_user())
        return '', 204
    return failure_response('Group Invite Not Found', 404)


@user.post('/reject_invite/<int:group_id>')
@authenticate(token_auth)
@response(EmptySchema, 204, 'Group invite rejected')
@other_responses({404: 'Invalid Group Invite'})
def reject_group_invite(group_id):
    """
    Reject Group Invite
    Rejects an invite to join a happiness group \n
    Requires: group ID is valid and corresponds to a group that has invited the user
    """
    group = get_group_by_id(group_id)
    if group is not None and group in token_auth.current_user().invites:
        group.remove_users([token_auth.current_user().username])
        return '', 204
    return failure_response('Group Invite Not Found', 404)


@user.delete('/')
@authenticate(token_auth)
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
    If the setting already exists in the property bag, it can enable or disable the setting. \n
    Returns: A JSON success response that contains the added setting, or a failure response.
    """
    current_user = token_auth.current_user()
    key, enabled, value = req.get("key"), req.get("enabled"), req.get("value")
    old_setting = Setting.query.filter(
        Setting.user_id == current_user.id, Setting.key == key).first()
    if old_setting is None:
        if value is None:
            new_setting = Setting(key=key, enabled=enabled,
                                  user_id=current_user.id)
        else:
            new_setting = Setting(key=key, enabled=enabled,
                                  value=value, user_id=current_user.id)
        db.session.add(new_setting)
        db.session.commit()
        return new_setting

    old_setting.enabled = enabled
    if value is not None:
        old_setting.value = value
    db.session.commit()
    return old_setting


@user.get('/settings/')
@authenticate(token_auth)
@response(SettingsSchema(many=True))
def get_user_settings():
    """
    Get Settings
    Gets the settings of the current user by authorization token. \n
    Returns: A JSON response of a list of keys, booleans, and values that contain setting keys, whether they are enabled/disabled, and specific values for the user.
    """
    current_user = token_auth.current_user()
    settings = Setting.query.filter(Setting.user_id == current_user.id).all()
    return settings


@user.post('/username/')
@authenticate(token_auth)
@body(UsernameSchema)
@response(UserSchema)
@other_responses({400: "Username already exists."})
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


@user.post('/reset_password/<token>')
@body(PasswordResetSchema)
@response(EmptySchema, 204, 'Password reset successful')
@other_responses({400: "Invalid password reset token"})
def reset_password(req, token):
    """
    Reset Password from Token
    This function was written under the assumption that when the user receives a verify password email,
    they would be redirected to a page where they are prompted to enter a new password. Then from this page they
    make a post request to the backend with their new intended password.
    """
    # Verify token is not expired
    email = confirm_email_token(token)
    if email is False:
        return failure_response("Token expired", 400)
    current_user = users_dao.get_user_by_email(email)
    if not current_user:
        return failure_response("Password reset token verification failed, token may be expired", 401)

    current_user.set_password(req.get("password"))
    db.session.commit()
    return '', 204


@user.post('/initiate_password_reset/')
@body(PasswordResetReqSchema)
@response(EmptySchema, 204, 'Password reset email sent')
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
        return failure_response("User associated with email address not found", 404)
    threading.Thread(target=email_methods.send_password_reset_email,
                     args=(user_by_email,)).start()
    return '', 204


@user.get('/self/')
@authenticate(token_auth)
@response(UserSchema)
def get_self():
    """
    Get Self
    Returns: the user object corresponding to the currently logged-in user.
    """
    return token_auth.current_user()
