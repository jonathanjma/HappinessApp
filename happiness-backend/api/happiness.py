from flask import Blueprint, json, request
from api.models import Happiness
from api.responses import success_response, failure_response
from api.app import db
from api import happiness_dao
from api.token import token_auth
from datetime import datetime
from sqlalchemy import delete

happiness = Blueprint('happiness', __name__)


@happiness.post('/')
@token_auth.login_required
def create_happiness():
    body = json.loads(request.data)
    current_user = token_auth.current_user()
    value, comment, timestamp = body.get(
        "value"), body.get("comment"), body.get("timestamp")
    if value is None:
        return failure_response("Please submit a value!")
    if timestamp is None:
        return failure_response("Error. Please try again!")

    # check if date already exists, rn used to avoid errors when debugging
    if happiness_dao.get_happiness_by_date(current_user.id, datetime.strptime(timestamp, "%Y-%m-%d")):
        return failure_response("Date already exists.")

    happiness = Happiness(user_id=current_user.id, value=value,
                          comment=comment, timestamp=datetime.strptime(timestamp, "%Y-%m-%d"))
    db.session.add(happiness)
    db.session.commit()
    return success_response(happiness.serialize(), 201)


@happiness.put('/<int:id>')
@token_auth.login_required
def edit_happiness(id):
    user_id = token_auth.current_user().id

    query_data = happiness_dao.get_happiness_by_id(id)
    if query_data:
        if query_data.user_id != user_id:
            return failure_response("Unauthorized.")
        value = request.args.get("value")
        comment = request.args.get("comment")
        if value:
            query_data.value = value
        if comment:
            query_data.comment = comment
        db.session.commit()
        return success_response(query_data.serialize(), 201)
    return failure_response("Data not found.")


@happiness.delete('/<int:id>')
@token_auth.login_required
def delete_happiness(id):
    """
    Deletes the happiness data corresponding to a specific id.
    Requires: user must be logged in
    :return: A success message with the delete information, or a failure response with the appropriate message."""
    happiness = happiness_dao.get_happiness_by_id(id)
    if not happiness:
        return failure_response("Happiness not found.")
    if happiness.user_id == token_auth.current_user().id:
        db.session.delete(happiness)
        db.session.commit()
        return success_response(happiness.serialize(), 200)
    return failure_response("Unauthorized.")


@happiness.get('/')
@token_auth.login_required
def get_happiness():
    """
    Gets the happiness of values of a given user between a specified start and end time. Requires: the time represented by start comes before the end
    :return: A JSON response of a list of key value pairs that contain each day's happiness value, comment, and timestamp.
    """
    today = datetime.strftime(datetime.today(), "%Y-%m-%d")
    user_id = request.args.get("user_id")
    start = request.args.get("start", "2023-01-01")
    end = request.args.get("end", today)
    stfor = datetime.strptime(start, "%Y-%m-%d")
    enfor = datetime.strptime(end, "%Y-%m-%d")

    # TODO check if user with given user_id is friend of the current user
    query_data = happiness_dao.get_happiness_by_range(user_id, stfor, enfor)
    special_list = [(datetime.strftime(h.timestamp, "%Y-%m-%d"), h.value, h.comment)
                    for h in query_data]
    return success_response({"happiness": special_list})


@happiness.get('/count/')
@token_auth.login_required
def get_paginaged_happiness():
    user_id = request.args.get("user_id")
    page = request.args.get("page", 1, type=int)
    count = request.args.get("count", 10, type=int)

    # TODO check if user with user_id is friend of current user
    query_data = happiness_dao.get_happiness_by_count(
        user_id, page, count)
    special_list = [(datetime.strftime(h.timestamp, "%Y-%m-%d"), h.value, h.comment)
                    for h in query_data]
    return success_response({"happiness": special_list})
