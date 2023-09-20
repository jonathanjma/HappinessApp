from datetime import datetime

from apifairy import authenticate, body, arguments, response, other_responses
from flask import Blueprint, request, current_app

from api.app import db
from api.dao import happiness_dao, users_dao
from api.dao.users_dao import get_user_by_id
from api.models.models import Happiness, Comment
from api.models.schema import HappinessSchema, HappinessEditSchema, HappinessGetTimeSchema, \
    HappinessGetCountSchema, HappinessRangeSchema, \
    HappinessGetQuery, CommentSchema, HappinessGetBySchema
from api.routes.token import token_auth
from api.util.errors import failure_response

happiness = Blueprint('happiness', __name__)


@happiness.post('/')
@authenticate(token_auth)
@body(HappinessSchema)
@response(HappinessSchema, 201)
@other_responses({400: "Date already exists or malformed input."})
def create_happiness(req):
    """
    Create Happiness Entry
    Creates a new happiness entry with a given value. \n
    Optional values: comment, timestamp (defaults to current day) \n
    Requires: Happiness value must be between 0 and 10 in 0.5 increments.
    Timestamp must be given in the %Y-%m-%d format.
    If the user has already submitted a happiness entry for the specified day, the entry will be overwritten. \n
    Returns: Happiness entry with the given information.
    """
    current_user = token_auth.current_user()
    today = datetime.strftime(datetime.today(), "%Y-%m-%d")
    value, comment, timestamp = req.get("value"), req.get("comment"), req.get("timestamp", today)

    # validate timestamp format
    try:
        timestamp = datetime.strptime(timestamp, "%Y-%m-%d")
    except ValueError:
        return failure_response("Timestamp must be given in the YYYY-MM-DD format.", 400)

    # check if date already exists
    potential_happiness = happiness_dao.get_happiness_by_date(current_user.id, timestamp)
    if potential_happiness:
        potential_happiness.comment = comment
        potential_happiness.value = value
        db.session.commit()
        return potential_happiness

    # validate happiness value
    if not (value * 2).is_integer() or value < 0 or value > 10:
        return failure_response("Invalid happiness value.", 400)

    happiness = Happiness(user_id=current_user.id, value=value, comment=comment, timestamp=timestamp)
    db.session.add(happiness)
    db.session.commit()
    return happiness


@happiness.put('/')
@authenticate(token_auth)
@arguments(HappinessGetBySchema)
@body(HappinessEditSchema)
@response(HappinessSchema)
@other_responses({403: "Not Allowed.", 404: "Happiness Not Found.", 400: "Insufficient Info."})
def edit_happiness(args, req):
    """
    Edit Happiness
    Given a ID or date for a specific happiness entry and a new comment or happiness value,
    modify the happiness entry corresponding to the ID/date with the new values.
    Happiness entry must have been created by the current user. \n
    Requires: ID must be valid, either value or comment sent. Date in YYYY-MM-DD format. \n
    Returns: Happiness entry with updated information.
    """
    id, date = args.get("id"), args.get("date")
    user_id = token_auth.current_user().id
    if id is not None:
        query_data = happiness_dao.get_happiness_by_id(id)
    elif date is not None:
        try:  # validate timestamp format
            date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return failure_response("Timestamp must be given in the YYYY-MM-DD format.", 400)
        query_data = happiness_dao.get_happiness_by_date(user_id, date)
    else:
        return failure_response('Insufficient Information', 400)

    if query_data:
        if query_data.user_id != user_id:
            return failure_response("Not Allowed.", 403)
        value, comment = req.get("value"), req.get("comment")
        if value != query_data.value and value is not None:
            query_data.value = value
        if comment:
            query_data.comment = comment
        db.session.commit()
        return query_data
    return failure_response("Happiness Not Found.", 404)


@happiness.delete('/')
@arguments(HappinessGetBySchema)
@authenticate(token_auth)
@other_responses({403: "Not Allowed.", 404: "Happiness Not Found.", 400: "Insufficient Info."})
def delete_happiness(args):
    """
    Delete Happiness
    Deletes the happiness entry corresponding to a specific ID or date (in YYYY-MM-DD format). \n
    Requires: Happiness entry must have been created by the current user.
    """
    id, date = args.get("id"), args.get("date")
    user_id = token_auth.current_user().id
    if id is not None:
        query_data = happiness_dao.get_happiness_by_id(id)
    elif date is not None:
        try:  # validate timestamp format
            date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return failure_response("Timestamp must be given in the YYYY-MM-DD format.", 400)
        query_data = happiness_dao.get_happiness_by_date(user_id, date)
    else:
        return failure_response('Insufficient Information', 400)

    if query_data:
        if query_data.user_id != user_id:
            return failure_response("Not Allowed.", 403)
        db.session.delete(query_data)
        db.session.commit()
        return "", 204
    return failure_response("Happiness Not Found.", 404)


@happiness.get('/')
@authenticate(token_auth)
@arguments(HappinessGetTimeSchema)
@response(HappinessSchema(many=True))
@other_responses({403: "Not Allowed.", 400: "Malformed Date."})
def get_happiness_time(req):
    """
    Get Happiness by Time Range
    Gets the happiness of values of a given user between a specified start and end date (inclusive).
    User must share a group with the user they are viewing. \n
    Requires: Start date is provided and comes before the end date.
    Dates must be given in the YYY-MM-DD format. \n
    Returns: List of all happiness entries between start and end date in sequential order
    """
    user_id = token_auth.current_user().id
    today = datetime.strftime(datetime.today(), "%Y-%m-%d")
    start, end, id = req.get("start"), req.get("end", today), req.get("id", user_id)

    # validate timestamp format
    try:
        stfor = datetime.strptime(start, "%Y-%m-%d")
        enfor = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return failure_response("Timestamp must be given in the YYYY-MM-DD format.", 400)

    if user_id == id or token_auth.current_user().has_mutual_group(users_dao.get_user_by_id(id)):
        return happiness_dao.get_happiness_by_timestamp(id, stfor, enfor)
    return failure_response("Not Allowed.", 403)


@happiness.get('/count')
@authenticate(token_auth)
@arguments(HappinessGetCountSchema)
@response(HappinessSchema(many=True))
@other_responses({403: "Not Allowed."})
def get_paginated_happiness(req):
    """
    Get Happiness by Count
    Gets a specified number of happiness values in reverse order.
    User must share a group with the user they are viewing. \n
    Paginated based on page number and happiness entries per page. Defaults to page=1 and count=10. \n
    Returns: Specified happiness entries in reverse order.
    """
    user_id = token_auth.current_user().id
    page, count, id = req.get("page", 1), req.get("count", 10), req.get("id", user_id)
    if user_id == id or token_auth.current_user().has_mutual_group(users_dao.get_user_by_id(id)):
        return happiness_dao.get_happiness_by_count(id, page, count)
    return failure_response("Not Allowed.", 403)


@happiness.post('/<int:id>/comment')
@authenticate(token_auth)
@body(CommentSchema)
@response(CommentSchema, 201)
@other_responses({403: "Not Allowed.", 404: "Happiness Not Found."})
def create_comment(req, id):
    """
    Create Discussion Comment
    Creates a happiness discussion comment for the specified happiness entry with the given text.
    User must share a group with the user who created the happiness entry. \n
    Requires: ID must be valid, comment text must be non-empty \n
    Returns: Comment created with the given information.
    """
    user_id = token_auth.current_user().id
    happiness_obj = happiness_dao.get_happiness_by_id(id)
    if happiness_obj:
        if token_auth.current_user().has_mutual_group(users_dao.get_user_by_id(happiness_obj.user_id)):
            comment = Comment(happiness_id=id, user_id=user_id, text=req.get("text"))
            db.session.add(comment)
            db.session.commit()
            return comment
        return failure_response("Not Allowed.", 403)
    return failure_response("Happiness Not Found.", 404)


@happiness.get('/<int:id>/comments')
@authenticate(token_auth)
@response(CommentSchema(many=True))
@other_responses({403: "Not Allowed.", 404: "Happiness Not Found."})
def get_comments(id):
    """
    Get Discussion Comments
    Gets all the discussion comments for a happiness entry. \n
    User must share a group with the user who created the happiness entry. \n
    Returns: List of discussion comments, only including the comments where
    the commenter shares a group with the current user
    """
    happiness_obj = happiness_dao.get_happiness_by_id(id)
    if happiness_obj:
        if token_auth.current_user().has_mutual_group(get_user_by_id(happiness_obj.user_id)):
            # only show comments if the commenter shares a group with the current user
            filtered = []
            for comment in happiness_obj.discussion_comments:
                if token_auth.current_user().has_mutual_group(get_user_by_id(comment.user_id)):
                    filtered.append(comment)
            return filtered
        return failure_response("Not Allowed.", 403)
    return failure_response("Happiness Not Found.", 404)


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
    page, count, target_user_id, query = req.get("page", 1), req.get("count", 10), \
        req.get("id", user_id), req.get("query")
    if user_id == target_user_id or my_user_obj.has_mutual_group(users_dao.get_user_by_id(target_user_id)):
        query_data = happiness_dao.get_paginated_happiness_by_query(target_user_id, query, page, count)
        return query_data
    return failure_response("Not Allowed.", 403)


@happiness.get('/export')
@authenticate(token_auth)
def export_happiness():
    """
    Export Happiness
    Exports a user's happiness, emailing the user with a CSV file attached, containing their comment, value, and timestamp.
    """
    current_user = token_auth.current_user()
    current_app.job_queue.enqueue("jobs.jobs.export_happiness", current_user.id)
    return "Happiness entries exported"


@happiness.post('/import')
def import_happiness():
    happiness_objs = []
    for entry in request.json:
        happiness_objs.append(
            Happiness(user_id=entry['user_id'], value=entry['value'], comment=entry.get('comment'),
                      timestamp=datetime.strptime(entry['timestamp'], "%Y-%m-%d")))
    db.session.add_all(happiness_objs)
    db.session.commit()

    return str(len(happiness_objs)) + ' happiness entries imported'

@happiness.get('/range')
@body(HappinessRangeSchema)
@response(HappinessSchema(many=True))
@authenticate(token_auth)
def get_happiness_from_value_range(req):
    """
    Gets all happiness objects for a user which all have happiness values within a specified range (low, high).
    Is paginated.
    Requires: User is logged in, high>=low, low,high are of type int.
    Returns: a list of happiness objects for a user which all have values within a range
    """
    user_id = token_auth.current_user().id
    low, high, id, page, count = req.get("low"), req.get("high"), req.get("id", user_id), \
        req.get("page", 1), req.get("count", 10)

    if user_id == id or token_auth.current_user().has_mutual_group(users_dao.get_user_by_id(id)):
        return happiness_dao.get_happiness_by_value_range(id, page, count, low, high)
    return failure_response("Not Allowed.", 403)
