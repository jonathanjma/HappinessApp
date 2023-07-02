import csv
import os
import uuid
from datetime import datetime

from apifairy import authenticate, body, arguments, response, other_responses
from flask import Blueprint, request, current_app, send_file

from api import happiness_dao, users_dao
from api.app import db
from api.models import Happiness
from api.responses import success_response, failure_response
from api.schema import HappinessSchema, HappinessEditSchema, HappinessGetTime, HappinessGetCount, HappinessGetQuery
from api.token import token_auth

happiness = Blueprint('happiness', __name__)


@happiness.post('/')
@authenticate(token_auth)
@body(HappinessSchema)
@response(HappinessSchema, 201)
@other_responses({400: "Date already exists.", 400: "Invalid happiness value."})
def create_happiness(req):
    """
    Create Happiness Entry
    Creates a new happiness entry with a given value. \n
    Optional values: comment, timestamp (default: current day) \n
    Returns: Happiness entry with the given information.
    Requires: Happiness entry must be between 0 and 10 in a 0.5 increment.
    """
    current_user = token_auth.current_user()
    value, comment, timestamp = req.get(
        "value"), req.get("comment"), req.get("timestamp")

    # check if date already exists, rn used to avoid errors when debugging
    if happiness_dao.get_happiness_by_date(current_user.id, datetime.strptime(timestamp, "%Y-%m-%d")):
        return failure_response("Date already exists.", 400)

    # validate happiness value
    # if float(value * 2).is_integer or value < 0 or value > 10:
    #     return failure_response("Invalid happiness value.", 400)

    happiness = Happiness(user_id=current_user.id, value=value,
                          comment=comment, timestamp=datetime.strptime(timestamp, "%Y-%m-%d"))
    db.session.add(happiness)
    db.session.commit()
    return happiness


@happiness.put('/<int:id>')
@authenticate(token_auth)
@body(HappinessEditSchema)
@response(HappinessSchema)
@other_responses({403: "Not Allowed.", 404: "Happiness Not Found."})
def edit_happiness(req, id):
    """
    Edit Happiness by ID
    Given a ID for a specific happiness entry and a new comment or happiness value,
    modify the happiness entry corresponding to the ID with the new values.
    Happiness entry must have been created by the current user. \n
    Requires: ID must be valid, either value or comment sent. \n
    Returns: Happiness entry with updated information.
    """
    user_id = token_auth.current_user().id
    query_data = happiness_dao.get_happiness_by_id(id)
    if query_data:
        if query_data.user_id != user_id:
            return failure_response("Not Allowed.", 403)
        value, comment = req.get("value"), req.get("comment")
        if value != query_data.value and value != None:
            query_data.value = value
        if comment:
            query_data.comment = comment
        db.session.commit()
        return query_data
    return failure_response("Happiness Not Found.", 404)


@happiness.delete('/<int:id>')
@authenticate(token_auth)
@other_responses({403: "Not Allowed.", 404: "Happiness Not Found."})
def delete_happiness(id):
    """
    Delete Happiness by ID
    Deletes the happiness entry corresponding to a specific ID. \n
    Requires: Happiness entry must have been created by the current user.
    """
    happiness = happiness_dao.get_happiness_by_id(id)
    if not happiness:
        return failure_response("Happiness Not Found.", 404)
    if happiness.user_id == token_auth.current_user().id:
        db.session.delete(happiness)
        db.session.commit()
        return "", 204
    return failure_response("Not Allowed.", 403)


@happiness.get('/')
@authenticate(token_auth)
@arguments(HappinessGetTime)
@response(HappinessSchema(many=True))
@other_responses({403: "Not Allowed."})
def get_happiness_time(req):
    """
    Get Happiness by Time Range
    Gets the happiness of values of a given user between a specified start and end date.
    User must share a group with the user they are viewing. \n
    Requires: the time represented by start comes before the end \n
    Returns: List of all happiness entries between start and end date in sequential order
    """
    user_id = token_auth.current_user().id
    my_user_obj = users_dao.get_user_by_id(user_id)
    today = datetime.strftime(datetime.today(), "%Y-%m-%d")
    start, end, id = req.get(
        "start", "2023-01-01"), req.get("end", today), req.get("id", user_id)
    stfor = datetime.strptime(start, "%Y-%m-%d")
    enfor = datetime.strptime(end, "%Y-%m-%d")

    if user_id == id or my_user_obj.has_mutual_group(users_dao.get_user_by_id(id)):
        query_data = happiness_dao.get_happiness_by_timestamp(
            id, stfor, enfor)
        return query_data
    return failure_response("Not Allowed.", 403)


@happiness.get('/count')
@authenticate(token_auth)
@arguments(HappinessGetCount)
@response(HappinessSchema(many=True))
@other_responses({403: "Not Allowed."})
def get_paginated_happiness(req):
    """
    Get Happiness by Count
    Gets a specified number of happiness values in reverse order.
    User must share a group with the user they are viewing. \n
    Paginated based on page number and happiness entries per page. Defaults to page=1 and count=10. \n
    Returns: Specified number of happiness entries in reverse order.
    """
    user_id = token_auth.current_user().id
    my_user_obj = users_dao.get_user_by_id(user_id)
    page, count, id = req.get("page", 1), req.get(
        "count", 10), req.get("id", user_id)
    if user_id == id or my_user_obj.has_mutual_group(users_dao.get_user_by_id(id)):
        query_data = happiness_dao.get_happiness_by_count(id, page, count)
        return query_data
    return failure_response("Not Allowed.", 403)


@happiness.get('/search')
@authenticate(token_auth)
@body(HappinessGetQuery)
@response(HappinessSchema(many=True))
@other_responses({403: "Not Allowed."})
def search_happiness(req):
    """
    Search Happiness
    Gets paginated data for happiness entries related by their journal entries to a specific query.
    Count, id, and page are optional, and will default to 10, current logged-in user's id, and 1 respectively.

    Returns: Happiness entries related to the user's query
    """
    user_id = token_auth.current_user().id
    my_user_obj = users_dao.get_user_by_id(user_id)
    page, count, target_user_id, query = req.get("page", 1), req.get(
        "count", 10), req.get("id", user_id), req.get("query")
    if user_id == target_user_id or my_user_obj.has_mutual_group(users_dao.get_user_by_id(target_user_id)):
        query_data = happiness_dao.get_paginated_happiness_by_query(target_user_id, query, page, count)
        return query_data
    return failure_response("Not Allowed.", 403)


@happiness.get('/export')
@authenticate(token_auth)
def export_happiness():
    """
    Export Happiness
    Exports a user's happiness, returning a CSV file containing the values, comments, and timestamps.
    One issue with this function is that it does not delete the CSV file after the request.
    I've tried a few ways of dealing with this issue, but it always deletes the file too late or cannot send the file.
    According to this stackoverflow the best way to do this is a cron job to periodically delete files in the folder
    based on their creation date. We can do this once we start working out how to do cron jobs.
    https://stackoverflow.com/q/24612366
    """
    current_user = token_auth.current_user()
    entries = happiness_dao.get_user_happiness(current_user.id)

    def to_dict_entry(n):
        new_dict = n.__dict__
        new_dict.pop('_sa_instance_state')
        new_dict.pop('user_id')
        new_dict.pop('id')

        return new_dict

    entries_dict = map(to_dict_entry, entries)
    fields = ['value', 'comment', 'timestamp']
    filename = f"happiness_{uuid.uuid4()}.csv"
    with open(f"./export/{filename}", 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(entries_dict)
    exports = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])

    return send_file(f"../export/{filename}", as_attachment=True)


@happiness.post('/import')
def import_happiness():
    happiness_objs = []
    for entry in request.json:
        happiness_objs.append(
            Happiness(user_id=entry['user_id'], value=entry['value'], comment=entry.get('comment'),
                      timestamp=datetime.strptime(entry['timestamp'], "%Y-%m-%d")))
    db.session.add_all(happiness_objs)
    db.session.commit()

    return success_response(str(len(happiness_objs)) + ' happiness entries imported')
