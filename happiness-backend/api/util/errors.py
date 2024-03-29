from flask import Blueprint, jsonify, abort
from werkzeug.http import HTTP_STATUS_CODES

errors = Blueprint('errors', __name__)


def failure_response(message: str, code: int):
    return abort(code, message)


def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


@errors.app_errorhandler(404)
def not_found_error(error):
    return error_response(404)


@errors.app_errorhandler(500)
def internal_error(error):
    return error_response(500)
