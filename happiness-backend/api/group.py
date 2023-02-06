from apifairy import authenticate, body, response, other_responses
from flask import Blueprint

from api.app import db
from api.models import Group
from api.responses import failure_response
from api.schema import CreateGroupSchema, EditGroupSchema, GroupSchema
from api.token import token_auth
from api.users_dao import get_group_by_id

group = Blueprint('group', __name__)


@group.post('/')
@authenticate(token_auth)
@body(CreateGroupSchema)
@response(GroupSchema, 201)
def create_group(req):
    """
    Create Group
    Creates a new group for users to share their happiness with each other.
    """

    new_group = Group(name=req['name'])
    new_group.users.append(token_auth.current_user())  # add group creator to group

    db.session.add(new_group)
    db.session.commit()

    return new_group


@group.put('/<int:group_id>')
@authenticate(token_auth)
@body(EditGroupSchema)
@response(GroupSchema)
@other_responses({404: 'Invalid Group', 403: 'Not Allowed'})
def edit_group(req, group_id):
    """
    Edit Group
    Edit a happiness group by changing its name, adding users, or removing users.
    """

    new_name, add_users, remove_users = req.get('new_name'), req.get('add_users'), \
        req.get('remove_users')
    if new_name is None and add_users is None and remove_users is None:
        return failure_response('Insufficient Information', 400)

    cur_user = token_auth.current_user()
    cur_group = get_group_by_id(group_id)
    if cur_group is None:
        return failure_response('Group Not Found', 404)
    elif cur_user not in cur_group.users:  # Only allow editing if user is member of group
        return failure_response('Not Allowed', 403)

    # Perform editing actions
    if new_name is not None and new_name != cur_group.name:
        cur_group.name = new_name
    if add_users is not None:
        add_usernames = list(map(lambda x: x['username'], add_users))
        cur_group.add_users(add_usernames)
    if remove_users is not None:
        rem_usernames = list(map(lambda x: x['username'], remove_users))
        cur_group.remove_users(rem_usernames)

    db.session.commit()

    return cur_group


@group.get('/<int:group_id>')
@authenticate(token_auth)
@response(GroupSchema)
@other_responses({404: 'Invalid Group'})
def group_info(group_id):
    """
    Get Group Info
    Get a happiness group's name and data about its users.
    """

    return get_group_by_id(group_id) or failure_response('Group Not Found', 404)


@group.delete('/<int:group_id>')
@authenticate(token_auth)
@other_responses({404: 'Invalid Group', 403: 'Not Allowed'})
def delete_group(group_id):
    """
    Delete Group
    Deletes a happiness group.
    """

    cur_user = token_auth.current_user()
    cur_group = get_group_by_id(group_id)
    if cur_group is None:
        return failure_response('Group Not Found', 404)
    elif cur_user not in cur_group.users:  # Only allow deletion if user is member of group
        return failure_response('Not Allowed', 403)

    db.session.delete(cur_group)
    db.session.commit()

    return '', 204
