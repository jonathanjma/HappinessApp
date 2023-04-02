import json

from flask import abort


def success_response(message, code=200):
    return json.dumps(message), code


def failure_response(message, code):
    return abort(code, message)
