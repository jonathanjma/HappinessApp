from datetime import datetime

import requests
from apifairy import authenticate, body, arguments, response, other_responses
from flask import Blueprint, current_app

from api.app import db
from api.authentication.auth import token_current_user
from api.dao import happiness_dao, users_dao
from api.dao.happiness_dao import get_happiness_by_id_or_date
from api.dao.users_dao import get_user_by_id
from api.models.models import Happiness, Comment
from api.models.schema import HappinessSchema, HappinessEditSchema, HappinessGetTimeSchema, \
    HappinessGetCountSchema, CommentSchema, DateIdGetSchema, HappinessMultiFilterSchema, CommentEditSchema, NumberSchema
from api.routes.token import token_auth
from api.util.errors import failure_response
from api.util.webhook import process_webhooks

happiness = Blueprint('happiness', __name__)


@happiness.post('/')
@authenticate(token_auth)
@body(HappinessSchema)
@response(HappinessSchema, 201)
@other_responses({400: "Malformed input."})
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
    current_user = token_current_user()
    today = datetime.today().date()
    value, comment, timestamp = req.get("value"), req.get("comment"), req.get("timestamp", today)

    # overwrite entry if date already exists
    happiness_obj = happiness_dao.get_happiness_by_date(current_user.id, timestamp)
    if happiness_obj:
        happiness_obj.comment = comment
        happiness_obj.value = value
        db.session.commit()
        process_webhooks(current_user, happiness_obj, True)
        return happiness_obj

    # validate happiness value
    if not (value * 2).is_integer() or value < 0 or value > 10:
        return failure_response("Invalid happiness value.", 400)

    # create new entry
    happiness = Happiness(user_id=current_user.id, value=value, comment=comment, timestamp=timestamp)
    db.session.add(happiness)
    db.session.commit()

    process_webhooks(current_user, happiness)

    return happiness


@happiness.put('/')
@authenticate(token_auth)
@arguments(DateIdGetSchema)
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
    query_data = get_happiness_by_id_or_date(args)
    if query_data:
        if query_data.user_id != token_current_user().id:
            return failure_response("Not Allowed.", 403)

        value, comment = req.get("value"), req.get("comment")
        if value != query_data.value and value is not None:
            # validate happiness value
            if not (value * 2).is_integer() or value < 0 or value > 10:
                return failure_response("Invalid happiness value.", 400)
            query_data.value = value
        if comment:
            query_data.comment = comment
        db.session.commit()
        process_webhooks(token_current_user(), query_data, True)
        return query_data
    return failure_response("Happiness Not Found.", 404)


@happiness.delete('/')
@arguments(DateIdGetSchema)
@authenticate(token_auth)
@other_responses({403: "Not Allowed.", 404: "Happiness Not Found.", 400: "Insufficient Info."})
def delete_happiness(args):
    """
    Delete Happiness
    Deletes the happiness entry corresponding to a specific ID or date (in YYYY-MM-DD format). \n
    Requires: Happiness entry must have been created by the current user.
    """
    query_data = get_happiness_by_id_or_date(args)
    if query_data:
        if query_data.user_id != token_current_user().id:
            return failure_response("Not Allowed.", 403)
        db.session.delete(query_data)
        db.session.commit()
        return "", 204
    return failure_response("Happiness Not Found.", 404)


@happiness.get('/')
@authenticate(token_auth)
@arguments(HappinessGetTimeSchema)
@response(HappinessSchema(many=True))
@other_responses({403: "Not Allowed."})
def get_happiness_date_range(req):
    """
    Get Happiness by Date Range
    Gets the happiness of values of a given user between a specified start and end date (inclusive).
    End date defaults to today. User must share a group with the user they are viewing. \n
    Requires: Start date is provided and comes before the end date.
    Dates must be given in the YYYY-MM-DD format. \n
    Returns: List of all happiness entries between start and end date in sequential order
    """
    user_id = token_current_user().id
    today = datetime.today().date()
    start, end, id = req.get("start"), req.get("end", today), req.get("id", user_id)

    if user_id == id or token_current_user().has_mutual_group(users_dao.get_user_by_id(id)):
        return happiness_dao.get_happiness_by_date_range([id], start, end)
    return failure_response("Not Allowed.", 403)


@happiness.get('/count')
@authenticate(token_auth)
@arguments(HappinessGetCountSchema)
@response(HappinessSchema(many=True))
@other_responses({403: "Not Allowed."})
def get_paginated_happiness(req):
    """
    Get Happiness by Count
    Gets the specified number of happiness values in reverse chronological order.
    Requires: User must share a group with the user they are viewing. \n
    Paginated based on page number and happiness entries per page. Defaults to page=1 and count=10. \n
    Returns: Specified happiness entries in reverse order.
    """
    user_id = token_current_user().id
    page, count, id = req.get("page", 1), req.get("count", 10), req.get("id", user_id)
    if user_id == id or token_current_user().has_mutual_group(users_dao.get_user_by_id(id)):
        return happiness_dao.get_happiness_by_count([id], page, count)
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
    user_id = token_current_user().id
    happiness_obj = happiness_dao.get_happiness_by_id(id)
    if happiness_obj:
        if token_current_user().has_mutual_group(users_dao.get_user_by_id(happiness_obj.user_id)):
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
    Requires: User must share a group with the user who created the happiness entry. \n
    Returns: List of discussion comments in ascending timestamp order, only including the
    comments where the commenter shares a group with the current user
    """
    happiness_obj = happiness_dao.get_happiness_by_id(id)
    if happiness_obj:
        if token_current_user().has_mutual_group(get_user_by_id(happiness_obj.user_id)):
            # only show comments if the commenter shares a group with the current user
            filtered = []
            for comment in happiness_obj.discussion_comments:
                if token_current_user().has_mutual_group(get_user_by_id(comment.user_id)):
                    filtered.append(comment)
            return filtered
        return failure_response("Not Allowed.", 403)
    return failure_response("Happiness Not Found.", 404)


@happiness.put('/comments/<int:id>')
@authenticate(token_auth)
@body(CommentEditSchema)
@response(CommentSchema)
@other_responses({404: 'Invalid Comment', 403: 'Not Allowed'})
def edit_comment(req, id):
    """
    Edit Discussion Comment
    Updates the text of a happiness discussion comment. \n
    Requires: User must be the author of the post they are editing.
    """
    comment_obj = happiness_dao.get_comment_by_id(id)
    if not comment_obj:
        return failure_response('Comment Not Found', 404)
    if comment_obj.user_id != token_current_user().id:
        return failure_response('Not Allowed', 403)

    comment_obj.text = req.get("data")
    db.session.commit()

    return comment_obj


@happiness.delete('/comments/<int:id>')
@authenticate(token_auth)
@other_responses({404: 'Invalid Comment', 403: 'Not Allowed'})
def delete_comment(id):
    """
    Delete Discussion Comment
    Deletes a happiness discussion comment. \n
    Requires: User must be the author of the post they are deleting.
    """
    comment_obj = happiness_dao.get_comment_by_id(id)
    if not comment_obj:
        return failure_response('Comment Not Found', 404)
    if comment_obj.user_id != token_auth.current_user().id:
        return failure_response('Not Allowed', 403)

    db.session.delete(comment_obj)
    db.session.commit()

    return '', 204


@happiness.get('/export')
@authenticate(token_auth)
def export_happiness():
    """
    Export Happiness
    Exports a user's happiness, emailing the user with a CSV file attached, containing their comment, value, and timestamp.
    """
    current_user = token_current_user()
    current_app.job_queue.enqueue("jobs.jobs.export_happiness", current_user.id)
    return "Happiness entries exported"


@happiness.get('/search')
@authenticate(token_auth)
@arguments(HappinessMultiFilterSchema)
@response(HappinessSchema(many=True))
def multi_filter_search_happiness(req):
    """
    Search Happiness
    Gets all happiness objects for a user that match the given constraints in the arguments including
    Date filter: entries are between [start] and [end] dates (inclusive)
    Value filter: entries are between [low] value and [high] value (inclusive)
    Text filter: entries contain [text]
    Each of these filters are optional to apply, but if no filters are applied, then the empty list is returned.
    Is paginated
    """
    user_id = req.get("user_id", token_auth.current_user().id)
    start, end = req.get("start"), req.get("end")
    low, high = req.get("low"), req.get("high")
    text = req.get("text")
    page, count = req.get("page", 1), req.get("count", 10)
    if not (user_id == token_auth.current_user().id or
            token_auth.current_user().has_mutual_group(users_dao.get_user_by_id(user_id))):
        return failure_response("Not Allowed.", 403)
    return happiness_dao.get_happiness_by_filter(user_id, page, count, start, end, low, high, text)


@happiness.get('/search/count')
@authenticate(token_auth)
@arguments(HappinessMultiFilterSchema)
@response(NumberSchema)
def count_multi_filter_search_happiness(req):
    """
    Count Searched Happiness
    Returns the number of happiness objects that match the filter of a given search request
    Date filter: entries are between [start] and [end] dates (inclusive)
    Value filter: entries are between [low] value and [high] value (inclusive)
    Text filter: entries contain [text]
    Each of these filters are optional to apply, but if no filters are applied, then 0 is returned 
    """
    user_id = req.get("user_id", token_auth.current_user().id)
    start, end = req.get("start"), req.get("end")
    low, high = req.get("low"), req.get("high")
    text = req.get("text")
    if not (user_id == token_auth.current_user().id or
            token_auth.current_user().has_mutual_group(users_dao.get_user_by_id(user_id))):
        return failure_response("Not Allowed.", 403)
    return {"number": happiness_dao.get_num_happiness_by_filter(user_id, start, end, low, high, text)}

@happiness.get('/wrapped')
@authenticate(token_auth)
@other_responses({400: "Not Allowed."})
def get_wrapped():
    """
    Get Happiness App Wrapped Data
    """
    all_wrapped_data = requests.get(current_app.config["WRAPPED_DATA_URL"]).json()
    if str(token_current_user().id) in all_wrapped_data.keys():
        return all_wrapped_data[str(token_auth.current_user().id)]
    return failure_response("Not Allowed.", 400)