from datetime import datetime

from apifairy import authenticate, body, arguments, response, other_responses
from flask import Blueprint
from api.errors import failure_response

from api.app import db
from api.dao.communities_dao import get_community_by_id
from api.dao.statistic_dao import get_statistic_by_timestamp, get_statistic_by_date, \
    get_statistic_by_id, get_statistic_by_count
from api.community import check_community

from api.models import Statistic
from api.schema import StatisticSchema, StatisticEditSchema, StatisticGetTimeSchema, StatisticGetCountSchema
from api.token import token_auth

statistic = Blueprint('statistic', __name__)


@statistic.post('/')
@body(StatisticSchema)
@response(StatisticSchema, 201)
@other_responses({400: "Date already exists or is malformed."})
def create_statistic(req):
    """
    Create Statistic Entry \n
    Creates a new statistic with the given statistics
    (mean, median, standard deviation, minimum, maximum, Q1, Q3) corresponding
    to a given community. \n
    Optional value: timestamp (defaults to current day) \n
    Requires: All values of the statistic must be non-null and between 0 and 10. 
    Community ID must be valid. Timestamp must be given in YYYY-MM-DD format. \n
    Returns: Statistic value with the given information.
    """
    today = datetime.strftime(datetime.today(), "%Y-%m-%d")
    community_id, mean, median, stdev, minval, maxval, firstquar, thirdquar, timestamp = req.get(
        "community_id"), req.get("mean"), req.get("median"), req.get("stdev"), req.get("minval"), req.get(
        "maxval"), req.get("firstquar"), req.get("thirdquar"), req.get("timestamp", today)

    # validate timestamp format
    try:
        timestamp = datetime.strptime(timestamp, "%Y-%m-%d")
    except ValueError:
        return failure_response("Timestamp must be given in the YYYY-MM-DD format.", 400)

    # check if date already exists
    if get_statistic_by_date(community_id, timestamp):
        return failure_response("Date already exists.", 400)

    statistic = Statistic(community_id=community_id, mean=mean, median=median,
                          stdev=stdev, minval=minval, maxval=maxval, firstquar=firstquar,
                          thirdquar=thirdquar, timestamp=timestamp)
    db.session.add(statistic)
    db.session.commit()
    return statistic


@statistic.put('/<int:id>')
@body(StatisticEditSchema)
@response(StatisticSchema)
@other_responses({404: "Statistic Not Found."})
def edit_statistic(req, id):
    """
    Edit Statistic by ID
    Given an ID for a specific statistic entry and a new statistic value (mean, 
    median, etc), modify the statistic corresponding to the ID with the new values. \n
    Requires: ID must be valid, new statistic(s) sent. \n
    Returns: Statistic entry with updated information.
    """
    query_data = get_statistic_by_id(id)
    if query_data:
        mean, median, stdev, minval, maxval, firstquar, thirdquar = req.get(
            "mean"), req.get("median"), req.get("stdev"), req.get("minval"), req.get(
            "maxval"), req.get("firstquar"), req.get("thirdquar")

        # perform editing
        if mean:
            query_data.mean = mean
        if median:
            query_data.median = median
        if stdev:
            query_data.stdev = stdev
        if minval:
            query_data.minval = minval
        if maxval:
            query_data.maxval = maxval
        if firstquar:
            query_data.firstquar = firstquar
        if thirdquar:
            query_data.thirdquar = thirdquar
        db.session.commit()
        return query_data
    return failure_response("Statistic Not Found.", 404)


@statistic.delete('/<int:id>')
@other_responses({404: "Happiness Not Found"})
def delete_statistic(id):
    """
    Delete Statistic
    Deletes the statistic corresponding to a specific ID. \n
    Requires: ID must be valid
    """
    query_data = get_statistic_by_id(id)
    if query_data:
        db.session.delete(query_data)
        return "", 204
    return failure_response("Statistic Not Found", 404)


@statistic.get('/')
@authenticate(token_auth)
@arguments(StatisticGetTimeSchema)
@response(StatisticSchema(many=True))
@other_responses({403: "Not Allowed.", 400: "Malformed Date.", 404: "Community Not Found."})
def get_statistic_time(req):
    """
    Get Statistic by Time Range \n
    Gets the statistics of a given community between a specified start and end date. \n
    Requires: start time is provided and comes before the end date, community ID is provided. Dates must be given in the YYYY-MM-DD format. \n
    Returns: List of all statistic entries between start and end date in sequential order
    """
    today = datetime.strftime(datetime.today(), "%Y-%m-%d")
    start, end, community_id = req.get("start"), req.get(
        "end", today), req.get("community_id")

    # validate timestamp
    try:
        stfor = datetime.strptime(start, "%Y-%m-%d")
        enfor = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return failure_response("Timestamp must be given in the YYYY-MM-DD format.", 400)

    check_community(get_community_by_id(community_id))

    return get_statistic_by_timestamp(community_id, stfor, enfor)


@statistic.get('/count')
@authenticate(token_auth)
@arguments(StatisticGetCountSchema)
@response(StatisticSchema(many=True))
@other_responses({403: "Not Allowed.", 404: "Community Not Found."})
def get_paginated_statistic(req):
    """
    Get Statistic by Count
    Gets a specified number of statistic values in reverse order. 
    User must be a member of the community whose statistics they are viewing. \n
    Paginated based on page number and statistic entries per page. Defaults to page=1 and count=10. \n
    Requires: Community ID is provided. \n
    Returns: Specified number of statistic values in reverse order.
    """
    page, count, community_id = req.get("page", 1), req.get(
        "count", 10), req.get("community_id")
    check_community(get_community_by_id(community_id))
    return get_statistic_by_count(community_id, page, count)
