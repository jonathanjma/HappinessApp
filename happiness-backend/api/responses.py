import json


def success_response(message, code=200):
    return json.dumps(message), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code
