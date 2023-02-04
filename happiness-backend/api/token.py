from flask import Blueprint
from flask import current_app
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from itsdangerous import URLSafeTimedSerializer

from api.app import db
from api.errors import error_response
from api.models import User

token = Blueprint('token', __name__)

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(username, password):
    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            return user


@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)


@token_auth.verify_token
def verify_token(session_token):
    if session_token:
        user = User.query.filter_by(session_token=session_token).first()
        if user and user.verify_session_token():
            return user


@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)


@token.post('/')
@basic_auth.login_required
def get_token():
    session_token = basic_auth.current_user().get_token()
    db.session.commit()

    return {'session_token': session_token}


@token.delete('/')
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()

    return '', 204


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email
