import random
from datetime import datetime

import pytest

from api import create_app
from api.app import db
from api.dao.groups_dao import get_group_by_id
from api.dao.users_dao import *
from api.models.models import Happiness
from config import TestConfig


@pytest.fixture
def init_client():
    app = create_app(TestConfig)

    client = app.test_client()
    with app.app_context():
        db.create_all()

        user1 = User(email='test1@example.app', username='user1', password='test')
        user2 = User(email='test2@example.app', username='user2', password='test')
        user3 = User(email='test3@example.app', username='user3', password='test')
        db.session.add_all([user1, user2, user3])
        db.session.commit()
        token_objs, tokens = zip(*[user1.create_token(), user2.create_token(), user3.create_token()])
        db.session.add_all(token_objs)
        db.session.commit()

        yield client, tokens


def auth_header(token):
    return {'Authorization': f'Bearer {token}'}


def user_in_group_json_model(username, json, group):
    return list(map(lambda x: x['username'], json['users'])).count(username) > 0 and \
        list(map(lambda x: x.username, group.users)).count(username) > 0


def invite_in_group_json_model(username, json, group):
    return list(map(lambda x: x['username'], json['invited_users'])).count(username) > 0 and \
        list(map(lambda x: x.username, group.invited_users)).count(username) > 0


def group_in_user_modal(group_id, user):
    return list(map(lambda x: x.id, user.groups)).count(group_id) > 0


def invite_in_user_modal(group_id, user):
    return list(map(lambda x: x.id, user.invites)).count(group_id) > 0


def test_create_group(init_client):
    client, tokens = init_client

    bad_group_create = client.post('/api/group/', json={}, headers=auth_header(tokens[0]))
    assert bad_group_create.status_code == 400

    group_create = client.post('/api/group/', json={'name': 'test'}, headers=auth_header(tokens[0]))
    assert group_create.status_code == 201
    new_group = get_group_by_id(1)
    assert new_group.name == group_create.json['name'] == 'test'
    assert user_in_group_json_model('user1', group_create.json, new_group)


def test_edit_group_name(init_client):
    client, tokens = init_client
    client.post('/api/group/', json={'name': 'test'}, headers=auth_header(tokens[0]))

    bad_group_edit = client.put('/api/group/1', json={}, headers=auth_header(tokens[0]))
    assert bad_group_edit.status_code == 400

    unauthorized_edit = client.put('/api/group/1', json={'name': 'sus'},
                                   headers=auth_header(tokens[1]))
    assert unauthorized_edit.status_code == 403

    name_edit = client.put('/api/group/1', json={'name': 'successful'},
                           headers=auth_header(tokens[0]))
    assert name_edit.status_code == 200
    assert name_edit.json['name'] == get_group_by_id(1).name == 'successful'


def test_edit_group_users(init_client):
    client, tokens = init_client
    client.post('/api/group/', json={'name': 'test'}, headers=auth_header(tokens[0]))

    invite_users = client.put('/api/group/1', json={
        'invite_users': ['user2', 'user3']
    }, headers=auth_header(tokens[0]))
    assert invite_users.status_code == 200
    assert len(invite_users.json['invited_users']) == len(get_group_by_id(1).invited_users) == 2
    assert invite_in_group_json_model('user2', invite_users.json, get_group_by_id(1))
    assert invite_in_group_json_model('user3', invite_users.json, get_group_by_id(1))
    assert not group_in_user_modal(1, get_user_by_id(2))
    assert invite_in_user_modal(1, get_user_by_id(2))

    unauthorized_edit = client.put('/api/group/1', json={'name': 'sus'},
                                   headers=auth_header(tokens[1]))
    assert unauthorized_edit.status_code == 403

    bad_accept_invite = client.post('/api/user/accept_invite/5', headers=auth_header(tokens[1]))
    assert bad_accept_invite.status_code == 404

    accept_invite = client.post('/api/user/accept_invite/1', headers=auth_header(tokens[1]))
    assert accept_invite.status_code == 204
    get_group = client.get('/api/group/1', headers=auth_header(tokens[1]))
    assert user_in_group_json_model('user2', get_group.json, get_group_by_id(1))
    assert group_in_user_modal(1, get_user_by_id(2))

    reject_invite = client.post('/api/user/reject_invite/1', headers=auth_header(tokens[2]))
    assert reject_invite.status_code == 204
    assert not invite_in_user_modal(1, get_user_by_id(3))

    client.put('/api/group/1', json={'invite_users': ['user3']}, headers=auth_header(tokens[0]))

    remove_users = client.put('/api/group/1', json={
        'remove_users': ['user1', 'user3']
    }, headers=auth_header(tokens[0]))
    assert remove_users.status_code == 200
    assert len(remove_users.json['users']) == len(get_group_by_id(1).users) == 1
    assert not user_in_group_json_model('user1', remove_users.json, get_group_by_id(1))
    assert not user_in_group_json_model('user3', remove_users.json, get_group_by_id(1))

    remove_last_user = client.put('/api/group/1', json={
        'remove_users': ['user2']
    }, headers=auth_header(tokens[1]))
    assert remove_last_user.status_code == 200
    assert get_group_by_id(1) is None
    assert not group_in_user_modal(1, get_user_by_id(3))


def test_group_info(init_client):
    client, tokens = init_client
    client.post('/api/group/', json={'name': ':-)'}, headers=auth_header(tokens[0]))
    client.put('/api/group/1', json={'invite_users': ['user2']}, headers=auth_header(tokens[0]))

    unauthorized_view = client.get('/api/group/1', headers=auth_header(tokens[2]))
    assert unauthorized_view.status_code == 403

    view = client.get('/api/group/1', headers=auth_header(tokens[1]))
    assert view.status_code == 200
    assert view.json['name'] == ':-)'
    assert user_in_group_json_model('user1', view.json, get_group_by_id(1))
    assert invite_in_group_json_model('user2', view.json, get_group_by_id(1))


def test_mutual_groups(init_client):
    client, tokens = init_client
    client.post('/api/group/', json={'name': ':-)'}, headers=auth_header(tokens[0]))
    assert not get_user_by_id(1).has_mutual_group(get_user_by_id(2))

    client.put('/api/group/1', json={'invite_users': ['user2']}, headers=auth_header(tokens[0]))
    assert not get_user_by_id(1).has_mutual_group(get_user_by_id(2))

    client.post('/api/user/accept_invite/1', headers=auth_header(tokens[1]))
    assert get_user_by_id(1).has_mutual_group(get_user_by_id(2))
    assert get_user_by_id(2).has_mutual_group(get_user_by_id(1))


def test_group_delete(init_client):
    client, tokens = init_client
    client.post('/api/group/', json={'name': ':-)'}, headers=auth_header(tokens[0]))
    client.put('/api/group/1', json={
        'invite_users': ['user2', 'user3']
    }, headers=auth_header(tokens[0]))
    client.post('/api/user/accept_invite/1', headers=auth_header(tokens[1]))
    assert group_in_user_modal(1, get_user_by_id(1)) and group_in_user_modal(1, get_user_by_id(2)) \
           and invite_in_user_modal(1, get_user_by_id(3))

    unauthorized_delete = client.delete('/api/group/1', headers=auth_header(tokens[2]))
    assert unauthorized_delete.status_code == 403

    delete = client.delete('/api/group/1', headers=auth_header(tokens[1]))
    assert delete.status_code == 204
    assert get_group_by_id(1) is None
    assert not group_in_user_modal(1, get_user_by_id(1)) and not group_in_user_modal(1, get_user_by_id(2)) \
           and not invite_in_user_modal(1, get_user_by_id(3))


def test_group_happiness(init_client):
    client, tokens = init_client
    client.post('/api/group/', json={'name': ':-)'}, headers=auth_header(tokens[0]))
    get_group_by_id(1).invite_users(['user2', 'user3'])
    get_group_by_id(1).add_user(get_user_by_id(2))
    get_group_by_id(1).add_user(get_user_by_id(3))

    happiness_in = []
    for user_id in range(1, 4):  # 1-3
        for date in range(1, 8):  # 1-7
            happiness_in.append(
                Happiness(user_id=user_id, value=random.randint(0, 10),
                          timestamp=datetime.strptime(f'2023-02-0{date}', '%Y-%m-%d')))
    db.session.add_all(happiness_in)
    db.session.commit()

    get_happiness_day1 = client.get('/api/group/1/happiness', query_string={
        'start': '2023-02-01',
        'end': '2023-02-01'
    }, headers=auth_header(tokens[0]))
    assert get_happiness_day1.status_code == 200
    assert len(get_happiness_day1.json) == 3

    get_happiness_week = client.get('/api/group/1/happiness', query_string={
        'start': '2023-02-01'
    }, headers=auth_header(tokens[0]))
    assert len(get_happiness_week.json) == 21
