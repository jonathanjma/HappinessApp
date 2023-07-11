from datetime import datetime

from apifairy import authenticate
from flask import Blueprint
from api.errors import failure_response

from api.app import db
from api.dao.communities_dao import get_community_by_id

from api.models import Community
from api.token import token_auth

# TODO: finish schemas


community = Blueprint('community', __name__)

# Makes sure requested community exists and user has permissions to access it,
# otherwise throws appropriate errors


def check_community(cur_community):
    if cur_community is None:
        return failure_response('Community Not Found', 404)

    # TODO: should users be able to see the statistics of communities they're not a part of?
    elif token_auth.current_user not in cur_community.users:
        return failure_response('Not Allowed', 403)


@community.post('/')
@authenticate(token_auth)
def create_community(req):
    """
    Create Community
    Creates a new happiness community with a given name. \n
    Requires: Community name \n
    Returns: JSON representation for the new community
    """

    new_community = Community(name=req['name'])
    # add community creator to community
    new_community.users.append(token_auth.current_user())

    db.session.add(new_community)
    db.session.commit()

    return new_community


@community.get('/<int:community_id>')
@authenticate(token_auth)
def community_info(community_id):
    """
    Get Community Info
    Get a happiness community's name and data about its users.
    User must be a member of the community they are viewing.
    Requires: valid community ID
    Returns: JSON representation for the requested community
    """

    # Return 404 if invalid community or 403 if user is not in community
    cur_community = get_community_by_id(community_id)
    check_community(cur_community)

    return cur_community


@community.get('/<int:group_id>/statistics')
@authenticate(token_auth)
def community_statistics(req, community_id):
    """
    Get Community Statistics
    Gets the statistics of a community between a specified start and end date (inclusive).
    User must be a member of the community they are viewing. \n
    Requires: valid community ID, the time represented by start date comes before the end date (which defaults to today) \n
    Returns: List of all statistics entries by day in the community between start and end date in sequential order
    """

    # Return 404 if invalid community or 403 if user is not in community
    cur_community = get_community_by_id(community_id)
    check_community(cur_community)

    today = datetime.strftime(datetime.today(), "%Y-%m-%d")
    start_date = datetime.strptime(req.get("start"), "%Y-%m-%d")
    end_data = datetime.strptime(req.get("end", today), "%Y-%m-%d")

    return get_statistics_by_group_timestamp()  # TODO: finish function
