from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

from api.dao.users_dao import get_user_by_username, get_token, get_user_by_id, get_user_by_email
from api.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(email_or_username, password):
    # First, assume user is logging in with their email.
    # If that fails, assume user is logging in with their username.
    if email_or_username and password:
        user = get_user_by_email(email_or_username)
        if user and user.verify_password(password):
            return user
        else:
            user = get_user_by_username(email_or_username)
            if user and user.verify_password(password):
                return user


@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)


@token_auth.verify_token
def verify_token(session_token):
    if session_token:
        token = get_token(session_token)
        if token and token.verify():
            return get_user_by_id(token.user_id)


@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)