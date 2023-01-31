from apifairy import body, response, other_responses
from flask import Blueprint

from api.app import db
from api.models import Group
from api.responses import failure_response
from api.schema import CreateGroupSchema, EditGroupSchema, GroupSchema
from api.user import check_logged_in
from api.users_dao import get_group_by_id

group = Blueprint('group', __name__)


@group.post('/')
@body(CreateGroupSchema)
@response(GroupSchema, 201)
def create_group(req):
    success, cur_user = check_logged_in()
    if not success or cur_user is None:
        return failure_response('Login Error', 401)

    new_group = Group(name=req['name'])
    new_group.users.append(cur_user)

    db.session.add(new_group)
    db.session.commit()

    return new_group


@group.put('/<int:group_id>')
@body(EditGroupSchema)
@response(GroupSchema)
@other_responses({404: "Invalid Group", 403: "Not Allowed"})
def edit_group(req, group_id):
    success, cur_user = check_logged_in()
    if not success or cur_user is None:
        return failure_response('Login Error', 401)

    new_name, add_users, remove_users = req.get('new_name'), req.get('add_users'), req.get(
        'remove_users')
    if new_name is None and add_users is None and remove_users is None:
        return failure_response('Insufficient Information', 400)

    cur_group = get_group_by_id(group_id)
    if cur_group is None:
        return failure_response('Group Not Found', 404)
    elif cur_user not in cur_group.users:
        return failure_response('Not Allowed', 403)

    if new_name is not None and new_name != cur_group.name:
        cur_group.name = new_name
    if add_users is not None:
        cur_group.add_users(add_users)
    if remove_users is not None:
        cur_group.remove_users(remove_users)

    db.session.commit()

    return cur_group


@group.get('/<int:group_id>')
@response(GroupSchema)
@other_responses({404: "Invalid Group"})
def group_info(group_id):
    success, cur_user = check_logged_in()
    if not success or cur_user is None:
        return failure_response('Login Error', 401)

    return get_group_by_id(group_id) or failure_response('Group Not Found', 404)


@group.delete('/<int:group_id>')
@other_responses({404: "Invalid Group", 403: "Not Allowed"})
def delete_group(group_id):
    success, cur_user = check_logged_in()
    if not success or cur_user is None:
        return failure_response('Login Error', 401)

    cur_group = get_group_by_id(group_id)
    if cur_group is None:
        return failure_response('Group Not Found', 404)
    elif cur_user not in cur_group.users:
        return failure_response('Not Allowed', 403)

    db.session.delete(cur_group)
    db.session.commit()

    return '', 204
