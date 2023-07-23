from datetime import datetime

from apifairy import authenticate, body, arguments, response, other_responses
from flask import Blueprint
from api.errors import failure_response

from api.app import db
from api.dao.communities_dao import get_community_by_id
from api.dao.statistic_dao import get_statistic_by_timestamp

from api.models import Community
from api.token import token_auth
from api.schema import CommunitySchema, CreateCommunitySchema, EditCommunitySchema, \
    StatisticSchema, HappinessGetTime


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
@body(CreateCommunitySchema)
@response(CommunitySchema, 201)
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
@response(CommunitySchema)
@other_responses({404: 'Invalid Community', 403: 'Not Allowed'})
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


@community.get('/<int:community_id>/statistics')
@authenticate(token_auth)
@arguments(HappinessGetTime)
@response(StatisticSchema(many=True))
@other_responses({404: 'Invalid Community', 403: 'Not Allowed'})
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
    end_date = datetime.strptime(req.get("end", today), "%Y-%m-%d")

    return get_statistic_by_timestamp(community_id, start_date, end_date)


@community.put('/<int:community_id>')
@authenticate(token_auth)
@body(EditCommunitySchema)
@response(CommunitySchema)
@other_responses({400: 'Insufficient Information', 404: 'Invalid Community', 403: 'Not Allowed'})
def edit_community(req, community_id):
    """
    Edit Community
    Edit a community by changing its name, adding users, or removing users.
    User must be a member of the community they are editing. \n
    Requires: valid community ID, at least one of: name, users to add, or users to remove \n
    Returns: JSON representation for the updated community
    """

    new_name, add_users, remove_users = req.get(
        'new_name'), req.get('add_users'), req.get('remove_users')
    if new_name is None and add_users is None and remove_users is None:
        return failure_response('Insufficient Information', 400)

    # Return 404 if invalid community or 403 if user is not in community
    cur_community = get_community_by_id(community_id)
    check_community(cur_community)

    # Perform editing actions
    if new_name is not None and new_name != cur_community.name:
        cur_community.name = new_name
    if add_users is not None:
        cur_community.add_users(add_users)
    if remove_users is not None:
        cur_community.remove_users(remove_users)

        # delete community if all users removed
        if len(cur_community.users) == 0:
            db.session.delete(cur_community)


@community.delete('/<int:community_id>')
@authenticate(token_auth)
@other_responses({404: 'Invalid Community', 403: 'Not Allowed'})
def delete_community(community_id):
    """
    Delete Commmunity
    Deletes a happiness community. Does not delete any user happiness information.
    User must be a full member of the community they are deleting. \n
    Requires: valid community ID
    """

    # Return 404 if invalid community or 403 if user is not in community
    cur_community = get_community_by_id(community_id)
    check_community(cur_community)

    # deletes entry from community table and user entries from association table
    db.session.delete(cur_community)
    db.session.commit()

    return '', 204
