import threading
import uuid
from datetime import datetime

import boto3
import filetype
from apifairy import authenticate, response, body, other_responses
from flask import Blueprint
from flask import current_app
from werkzeug.security import generate_password_hash

from api.dao import users_dao
from api import email_methods
from api.app import db
from api.email_token_methods import confirm_email_token
from api.models import User, Setting
from api.errors import failure_response
from api.schema import GroupSchema, UserSchema, CreateUserSchema, SettingsSchema, SettingInfoSchema, \
    SimpleUserSchema, FileUploadSchema, UserInfoSchema, PasswordResetReqSchema, \
    EmptySchema, PasswordResetSchema
from api.token import token_auth

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
@response(GroupSchema(many=True))
def user_groups():
    """
    Get Groups
    Returns: a list of happiness groups that the user is in as well as any they have been invited to join.
    """
    return token_auth.current_user().groups


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
    If the setting already exists in the property bag, it modifies the value of the setting. \n
    Returns: A JSON success response that contains the added setting, or a failure response.
    """
    current_user = token_auth.current_user()
    key, value = req.get("key"), req.get("value")
    old_setting = Setting.query.filter(Setting.user_id == current_user.id, Setting.key == key).first()
    if old_setting is None:
        new_setting = Setting(key=key, value=value, user_id=current_user.id)
        db.session.add(new_setting)
        db.session.commit()
        return new_setting

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
    Returns: A JSON response of a list of key value pairs that contain setting keys and their values for the user.
    """
    current_user = token_auth.current_user()
    settings = Setting.query.filter(Setting.user_id == current_user.id).all()
    return settings


@user.post('/info/')
@authenticate(token_auth)
@body(UserInfoSchema)
@response(SimpleUserSchema)
@other_responses({400: "Provided data already exists."})
def change_user_info(req):
    """
    Change User Info
    Changes a user's info based on 3 different `data_type`(s): \n
    "username" \n
    "email" \n
    "password" \n
    Then the associated data must be put in the `data` field of the request.
    """
    data_type = req.get("data_type")
    current_user = token_auth.current_user()

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

        new_password = req.get("data")
        current_user.password = generate_password_hash(new_password)
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
    res = s3.put_object(Bucket=current_app.config["AWS_BUCKET_NAME"], Body=data, Key=file_name, ACL="public-read")

    # Construct image URL and mutate user object to reflect new profile image URL:

    img_url = (f"https://{current_app.config['AWS_BUCKET_NAME']}.s3." +
               f"{current_app.config['AWS_REGION']}.amazonaws.com/{file_name}")
    current_user.profile_picture = img_url
    db.session.commit()

    return current_user
