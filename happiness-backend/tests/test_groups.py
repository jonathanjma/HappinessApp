import random
from datetime import datetime

import pytest

from api import create_app
from api.app import db
from api.groups_dao import get_group_by_id
from api.models import Happiness
from api.users_dao import *
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

        yield client, [user1.get_token(), user2.get_token(), user3.get_token()]


def auth_header(token):
    return {'Authorization': f'Bearer {token}'}


def in_group_modal(username, group):
    return list(map(lambda x: x.username, group.users)).count(username) > 0


def in_group_json(username, json):
    return list(map(lambda x: x['username'], json['users'])).count(username) > 0


def in_user_modal(group_id, user):
    return list(map(lambda x: x.id, user.groups)).count(group_id) > 0


def test_create_group(init_client):
    client, tokens = init_client

    bad_group_create = client.post('/api/group/', json={}, headers=auth_header(tokens[0]))
    assert bad_group_create.status_code == 400

    group_create = client.post('/api/group/', json={'name': 'test'}, headers=auth_header(tokens[0]))
    assert group_create.status_code == 201
    new_group = get_group_by_id(1)
    assert new_group.name == group_create.json['name'] == 'test'
    assert in_group_json('user1', group_create.json) and in_group_modal('user1', new_group)


def test_edit_group(init_client):
    client, tokens = init_client
    client.post('/api/group/', json={'name': 'test'}, headers=auth_header(tokens[0]))

    bad_group_edit = client.put('/api/group/1', json={}, headers=auth_header(tokens[0]))
    assert bad_group_edit.status_code == 400

    unauthorized_edit = client.put('/api/group/1', json={'new_name': 'sus'},
                                   headers=auth_header(tokens[1]))
    assert unauthorized_edit.status_code == 403

    name_edit = client.put('/api/group/1', json={'new_name': 'successful'},
                           headers=auth_header(tokens[0]))
    assert name_edit.status_code == 200
    assert name_edit.json['name'] == get_group_by_id(1).name == 'successful'

    add_users = client.put('/api/group/1', json={
        'add_users': ['user2', 'user3']
    }, headers=auth_header(tokens[0]))
    assert add_users.status_code == 200
    assert len(add_users.json['users']) == len(get_group_by_id(1).users) == 3
    assert in_group_json('user2', add_users.json) and in_group_modal('user2', get_group_by_id(1))
    assert in_group_json('user3', add_users.json) and in_group_modal('user3', get_group_by_id(1))

    remove_users = client.put('/api/group/1', json={
        'remove_users': ['user1', 'user2']
    }, headers=auth_header(tokens[0]))
    assert remove_users.status_code == 200
    assert len(remove_users.json['users']) == len(get_group_by_id(1).users) == 1
    assert not in_group_json('user1', remove_users.json) and not in_group_modal('user1',
                                                                                get_group_by_id(1))
    assert not in_group_json('user2', remove_users.json) and not in_group_modal('user2',
                                                                                get_group_by_id(1))

    remove_last_user = client.put('/api/group/1', json={
        'remove_users': ['user3']
    }, headers=auth_header(tokens[2]))
    assert remove_last_user.status_code == 200
    assert get_group_by_id(1) is None
    assert not in_user_modal(1, get_user_by_id(3))


def test_group_info(init_client):
    client, tokens = init_client
    client.post('/api/group/', json={'name': ':-)'}, headers=auth_header(tokens[0]))
    client.put('/api/group/1', json={
        'add_users': ['user2']
    }, headers=auth_header(tokens[0]))

    bad_view = client.get('/api/group/1', headers=auth_header(tokens[2]))
    assert bad_view.status_code == 403

    view = client.get('/api/group/1', headers=auth_header(tokens[1]))
    assert view.status_code == 200
    assert view.json['name'] == ':-)'
    assert in_group_json('user1', view.json) and in_group_json('user2', view.json)


def test_group_delete(init_client):
    client, tokens = init_client
    client.post('/api/group/', json={'name': ':-)'}, headers=auth_header(tokens[0]))
    client.put('/api/group/1', json={
        'add_users': ['user2']
    }, headers=auth_header(tokens[0]))
    assert in_user_modal(1, get_user_by_id(1)) and in_user_modal(1, get_user_by_id(2))

    bad_delete = client.delete('/api/group/1', headers=auth_header(tokens[2]))
    assert bad_delete.status_code == 403

    delete = client.delete('/api/group/1', headers=auth_header(tokens[1]))
    assert delete.status_code == 204
    assert get_group_by_id(1) is None
    assert not in_user_modal(1, get_user_by_id(1)) and not in_user_modal(1, get_user_by_id(2))


def test_group_happiness(init_client):
    client, tokens = init_client
    client.post('/api/group/', json={'name': ':-)'}, headers=auth_header(tokens[0]))
    client.put('/api/group/1', json={
        'add_users': ['user2']
    }, headers=auth_header(tokens[0]))

    happiness_in = []
    for user_id in range(1, 4):  # 1-3
        for date in range(1, 8):  # 1-7
            happiness_in.append(
                Happiness(user_id=user_id, value=random.randint(0, 10),
                          timestamp=datetime.strptime(f'2023-02-0{date}', '%Y-%m-%d')))
    db.session.add_all(happiness_in)
    db.session.commit()

    get_group_happiness = client.get('/api/group/1/happiness', query_string={
        'count': 30
    }, headers=auth_header(tokens[0]))
    assert get_group_happiness.status_code == 200
    assert len(get_group_happiness.json) == 14

    get_group_happiness_paginate = client.get('/api/group/1/happiness', query_string={
        'count': 10,
        'page': 1
    }, headers=auth_header(tokens[0]))
    assert len(get_group_happiness_paginate.json) == 10

    get_group_happiness_paginate2 = client.get('/api/group/1/happiness', query_string={
        'count': 10,
        'page': 2
    }, headers=auth_header(tokens[0]))
    assert len(get_group_happiness_paginate2.json) == 4
