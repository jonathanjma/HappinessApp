from apifairy import authenticate, response, other_responses
from flask import Blueprint, request
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

from api.models import Token
from api.responses import failure_response
from api.users_dao import get_user_by_username, get_user_by_id, get_token

from api.app import db
from api.errors import error_response
from api.schema import TokenSchema

token = Blueprint('token', __name__)

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(username, password):
    if username and password:
        user = get_user_by_username(username)
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


@token.post('/')
@authenticate(basic_auth)
@response(TokenSchema)
def new_token():
    """
    Get Token
    Creates a new session token for a user to access the Happiness App API. (Logs them in) \n
    Returns: a new session token for the user
    """
    token = basic_auth.current_user().create_token()
    db.session.add(token)
    Token.clean()
    db.session.commit()

    return token, 201


@token.delete('/')
@authenticate(token_auth)
@other_responses({401: "Invalid token"})
def revoke_token():
    """
    Revoke Token
    Expires a user's API access token. Equivalent to "logging out".
    """
    token = get_token(request.headers['Authorization'].split()[1])
    if token and token.user_id == token_auth.current_user().id:
        token.revoke()
        db.session.commit()
        return '', 204

    return failure_response('Invalid token', 401)
