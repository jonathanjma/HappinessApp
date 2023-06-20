from apifairy import authenticate, response, other_responses
from flask import Blueprint, request

from api.auth import basic_auth, token_auth
from api.models import Token
from api.dao.users_dao import get_token

from api.app import db
from api.errors import failure_response
from api.schema import TokenSchema

token = Blueprint('token', __name__)

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
