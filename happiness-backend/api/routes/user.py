import threading
import uuid
from datetime import datetime

import boto3
import filetype
from apifairy import authenticate, response, body, other_responses, arguments
from flask import Blueprint
from flask import current_app

from api.app import db
from api.authentication.email_token_methods import confirm_email_token
from api.dao import users_dao
from api.dao.groups_dao import get_group_by_id
from api.models.models import User, Setting
from api.models.schema import UserSchema, CreateUserSchema, SettingsSchema, SettingInfoSchema, \
    UserInfoSchema, PasswordResetReqSchema, SimpleUserSchema, EmptySchema, PasswordResetSchema, \
    FileUploadSchema, PasswordKeyOptSchema, UserGroupsSchema
from api.routes.token import token_auth
from api.util import email_methods
from api.util.errors import failure_response

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


@user.put('/info/')
@authenticate(token_auth)
@body(UserInfoSchema)
@arguments(PasswordKeyOptSchema, location='headers')
@response(SimpleUserSchema, headers=PasswordKeyOptSchema)
@other_responses({400: "Provided data already exists or empty data field."})
def change_user_info(req, headers):
    """
    Change User Info
    Changes a user's info based on 3 different `data_type`(s):
    - "username" (must be unique)
    - "email" (must be unique)
    - "password"
    - "key_recovery_phrase"
    Then the associated data must be put in the `data` field of the request. \n
    If changing password or adding/changing key_recovery_phrase, the user's `password_key`
    (provided by server during API token creation) must also be sent.
    """
    data_type = req.get("data_type")
    current_user = token_auth.current_user()

    if len(req.get("data")) == 0:
        return failure_response('Data is empty.', 400)

    if data_type == "username":
        # Change a user's username, which requires their username to be unique.
        new_username = req.get("data")
        similar_user = users_dao.get_user_by_username(new_username)
        if similar_user is not None:
            return failure_response("Provide data already exists", 400)

        current_user.username = new_username
        db.session.commit()
        return current_user
    elif data_type == "email":
        # Changes a user's email, which requires their email to be unique.
        new_email = req.get("data")
        similar_user = users_dao.get_user_by_email(new_email)
        if similar_user is not None:
            return failure_response("Provided data already exists", 400)

        current_user.email = new_email
        db.session.commit()
        return current_user
    elif data_type == "password":
        # Changes a user's password.
        try:
            current_user.change_password(req.get("data"), headers.get("password_key"))
            db.session.commit()
            return current_user, {
                'Password-Key': current_user.derive_pwd_key(req.get('data'))
            }
        except Exception as e:
            print(e)
            return failure_response('Invalid password key.', 400)
    elif data_type == "key_recovery_phrase":
        # Adds/Changes key recovery phrase to prevent loss of encrypted data on password reset.
        try:
            current_user.add_key_recovery(req.get("data"), headers.get("password_key"))
            db.session.commit()
            return current_user
        except Exception as e:
            print(e)
            return failure_response('Invalid password key.', 400)
    else:
        return failure_response('Unknown data_type.', 400)


@user.post('/reset_password/<token>')
@body(PasswordResetSchema)
@arguments(PasswordKeyOptSchema, location='headers')
@response(EmptySchema, 204, 'Password reset successful')
@other_responses({400: "Invalid password reset token or recovery input"})
def reset_password(req, headers, token):
    """
    Reset Password from Token
    This function was written under the assumption that when the user receives a verify password email,
    they would be redirected to a page where they are prompted to enter a new password. Then from this page they
    make a post request to the backend with their new intended password. \n

    If the user has previously added a key recovery phrase and provides their recovery phrase, their
    encrypted journal entries will not be lost. Otherwise, this will cause them to become lost
    (since they will never be able to be decrypted) and therefore will be deleted.
    """
    # Verify token is not expired
    email = confirm_email_token(token)
    if email is False:
        return failure_response("Token expired", 400)
    current_user = users_dao.get_user_by_email(email)
    if not current_user:
        return failure_response("Password reset token verification failed, token may be expired", 401)

    try:
        current_user.reset_password(req.get("password"),
                                    req.get("recovery_phrase"), headers.get('password_key'))
        db.session.commit()
        return '', 204
    except Exception as e:
        print(e)
        return failure_response('Invalid recovery input.', 400)


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


@user.post('/pfp/')
@authenticate(token_auth)
@response(SimpleUserSchema)
@body(FileUploadSchema, location='form')
@other_responses({400: "Invalid request"})
def add_pfp(req):
    """
    Add Profile Picture
    Route to change the user's profile picture.
    Takes an image from the request body, which should be the in the form of binary file data in the form-data section
    of the request body.
    """

    # Check valid user and valid image file

    data = req["file"].read()
    current_user = token_auth.current_user()
    # Check that data exists
    if not data:
        return failure_response("Invalid request", 400)
    # Check that data is an image file
    if not filetype.is_image(data):
        return failure_response("Invalid request", 400)
    # Check that data is under 10 megabytes
    if len(data) > 10000000:
        return failure_response("Invalid request", 400)

    # Connect to boto3

    boto_kwargs = {
        "aws_access_key_id": current_app.config["AWS_ACCESS"],
        "aws_secret_access_key": current_app.config["AWS_SECRET"],
        "region_name": current_app.config["AWS_REGION"]
    }
    s3 = boto3.Session(**boto_kwargs).client("s3")

    # Create unique file name and upload image to AWS:

    file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4()}.{(filetype.guess(data)).extension}"
    res = s3.put_object(
        Bucket=current_app.config["AWS_BUCKET_NAME"], Body=data, Key=file_name, ACL="public-read")

    # Construct image URL and mutate user object to reflect new profile image URL:

    img_url = (f"https://{current_app.config['AWS_BUCKET_NAME']}.s3." +
               f"{current_app.config['AWS_REGION']}.amazonaws.com/{file_name}")
    current_user.profile_picture = img_url
    db.session.commit()

    return current_user
