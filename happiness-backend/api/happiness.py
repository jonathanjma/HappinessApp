from flask import Blueprint
from api.models import User, Happiness
from api.responses import success_response, failure_response
from flask import json, request
from api.app import db
from api import users_dao
from api.user import extract_token
from datetime import datetime, timezone

happiness = Blueprint('happiness', __name__)


@happiness.post('/')
def create_happiness():
    body = json.loads(request.data)
    success, token = extract_token(request)
    if not success:
        return failure_response("Session token not found. Relog?")
    current_user = users_dao.get_user_by_session_token(token)
    if current_user is None or not current_user.verify_session_token(token):
        return failure_response("Current user not found. Relog?")

    value, comment, timestamp = body.get(
        "value"), body.get("comment"), body.get("timestamp")
    if value is None:
        return failure_response("Please submit a value!")
    if timestamp is None:
        return failure_response("Error. Please try again!")
    happiness = Happiness(user_id=current_user.id, value=value,
                          comment=comment, timestamp=datetime.strptime(timestamp, "%Y-%m-%d"))
    db.session.add(happiness)
    db.session.commit()
    return success_response(happiness.serialize(), 201)


@happiness.get('/')
def get_happiness():
    """
    Gets the happiness of values of a given user. Requires: the time represented by start comes before the end
    :return: A JSON response of a list of key value pairs that contain each day's happiness value, comment, and timestamp.
    """
    success, token = extract_token(request)
    today = datetime.strftime(datetime.today(), "%Y-%m-%d")
    user_id = request.args.get("user_id")
    start = request.args.get("start")
    end = request.args.get("end", today)
    stfor = datetime.strptime(start, "%Y-%m-%d")
    enfor = datetime.strptime(end, "%Y-%m-%d")
    if not success:
        return failure_response("Session token not found. Relog?")
    current_user = users_dao.get_user_by_session_token(token)
    if current_user is None or not current_user.verify_session_token(token):
        return failure_response("User with current session token not found. Relog?")
    # TODO check if user with given user_id is friend of the current user
    query_data = Happiness.query.filter(
        Happiness.user_id == user_id,
        Happiness.timestamp.between(stfor, enfor)).all()
    # return success_response("starttime: " + start + " and endtime: " + end)
    special_list = [(datetime.strftime(h.timestamp, "%Y-%m-%d"), h.value)
                    for h in query_data]
    special_list.sort()
    return success_response({"happiness": special_list})
