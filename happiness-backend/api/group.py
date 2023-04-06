from datetime import datetime

from apifairy import authenticate, body, arguments, response, other_responses
from flask import Blueprint

from api.app import db
from api.groups_dao import get_group_by_id
from api.happiness_dao import get_happiness_by_group_timestamp
from api.models import Group
from api.responses import failure_response
from api.schema import CreateGroupSchema, EditGroupSchema, GroupSchema, HappinessSchema, \
    HappinessGetTime
from api.token import token_auth

group = Blueprint('group', __name__)

# Makes sure requested group exists and user has permissions to view/edit it,
# otherwise throws appropriate errors
def check_group(cur_group):
    if cur_group is None:
        return failure_response('Group Not Found', 404)
    elif token_auth.current_user() not in cur_group.users:
        return failure_response('Not Allowed', 403)


@group.post('/')
@authenticate(token_auth)
@body(CreateGroupSchema)
@response(GroupSchema, 201)
def create_group(req):
    """
    Create Group
    Creates a new happiness group with a given name. \n
    Requires: group name \n
    Returns: JSON representation for the new group
    """

    new_group = Group(name=req['name'])
    new_group.users.append(token_auth.current_user())  # add group creator to group

    db.session.add(new_group)
    db.session.commit()

    return new_group


@group.get('/<int:group_id>')
@authenticate(token_auth)
@response(GroupSchema)
@other_responses({404: 'Invalid Group', 403: 'Not Allowed'})
def group_info(group_id):
    """
    Get Group Info
    Get a happiness group's name and data about its users.
    User must be a member of the group they are viewing. \n
    Requires: valid group ID \n
    Returns: JSON representation for the requested group
    """

    # Return 404 if invalid group or 403 if user is not in group
    cur_group = get_group_by_id(group_id)
    check_group(cur_group)

    return cur_group


@group.get('/<int:group_id>/happiness')
@authenticate(token_auth)
@arguments(HappinessGetTime)
@response(HappinessSchema(many=True))
@other_responses({404: 'Invalid Group', 403: 'Not Allowed'})
def group_happiness(req, group_id):
    """
    Get Group Happiness
    Gets the happiness of values of a group between a specified start and end date.
    User must be a member of the group they are viewing. \n
    Requires: valid group ID, the time represented by start date comes before the end date (which defaults to today) \n
    Returns: List of all happiness entries from users in the group between start and end date in sequential order
    """

    # Return 404 if invalid group or 403 if user is not in group
    cur_group = get_group_by_id(group_id)
    check_group(cur_group)

    today = datetime.strftime(datetime.today(), "%Y-%m-%d")
    start_date = datetime.strptime(req.get("start"), "%Y-%m-%d")
    end_data = datetime.strptime(req.get("end", today), "%Y-%m-%d")

    # page, count = req.get('page', 1), req.get('count', 10)
    # return get_happiness_by_group_count(list(map(lambda x: x.id, cur_group.users)), page, count)

    return get_happiness_by_group_timestamp(list(map(lambda x: x.id, cur_group.users)), start_date, end_data)

@group.put('/<int:group_id>')
@authenticate(token_auth)
@body(EditGroupSchema)
@response(GroupSchema)
@other_responses({400: 'Insufficient Information', 404: 'Invalid Group', 403: 'Not Allowed'})
def edit_group(req, group_id):
    """
    Edit Group
    Edit a happiness group by changing its name, adding users, or removing users.
    User must be a member of the group they are editing. \n
    Requires: valid group ID, at least one of: name, users to add, or users to remove \n
    Returns: JSON representation for the updated group
    """

    new_name, add_users, remove_users = req.get('new_name'), req.get('add_users'), \
        req.get('remove_users')
    if new_name is None and add_users is None and remove_users is None:
        return failure_response('Insufficient Information', 400)

    # Return 404 if invalid group or 403 if user is not in group
    cur_group = get_group_by_id(group_id)
    check_group(cur_group)

    # Perform editing actions
    if new_name is not None and new_name != cur_group.name:
        cur_group.name = new_name
    if add_users is not None:
        cur_group.add_users(add_users)
    if remove_users is not None:
        cur_group.remove_users(remove_users)

        # delete group if all users removed
        if len(cur_group.users) == 0:
            db.session.delete(cur_group)

    db.session.commit()

    return cur_group

@group.delete('/<int:group_id>')
@authenticate(token_auth)
@other_responses({404: 'Invalid Group', 403: 'Not Allowed'})
def delete_group(group_id):
    """
    Delete Group
    Deletes a happiness group. Does not delete any user happiness information.
    User must be a member of the group they are deleting. \n
    Requires: valid group ID
    """

    # Return 404 if invalid group or 403 if user is not in group
    cur_group = get_group_by_id(group_id)
    check_group(cur_group)

    # deletes entry from group table and user entries from association table
    db.session.delete(cur_group)
    db.session.commit()

    return '', 204
