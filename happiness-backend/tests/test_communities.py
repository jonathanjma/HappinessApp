import random
from datetime import datetime

import pytest
from flask import json

from api import create_app
from api.app import db
from api.dao.users_dao import *
from api.dao.communities_dao import *
from config import TestConfig


@pytest.fixture
def init_client():
    app = create_app(TestConfig)

    client = app.test_client()
    with app.app_context():
        db.create_all()

        user1 = User(email='test1@example.app',
                     username='user1', password='test')
        user2 = User(email='test2@example.app',
                     username='user2', password='test')
        user3 = User(email='test3@example.app',
                     username='user3', password='test')
        db.session.add_all([user1, user2, user3])
        db.session.commit()
        tokens = [user1.create_token(), user2.create_token(),
                  user3.create_token()]
        db.session.add_all(tokens)
        db.session.commit()

        yield client, [tokens[0].session_token, tokens[1].session_token, tokens[2].session_token]


def auth_header(token):
    return {'Authorization': f'Bearer {token}'}


def user_in_community_json_model(username, json, community):
    return list(map(lambda x: x['username'], json['users'])).count(username) > 0 and \
        list(map(lambda x: x.username, community.users)).count(username) > 0


def test_create_community(init_client):
    client, tokens = init_client

    bad_community_create = client.post(
        '/api/community/', json={}, headers=auth_header(tokens[0]))
    assert bad_community_create.status_code == 400

    community_create = client.post(
        '/api/community/', json={'name': 'test'}, headers=auth_header(tokens[0]))
    assert community_create.status_code == 201

    new_community = get_community_by_id(1)
    assert new_community.name == community_create.json['name'] == 'test'
    assert user_in_community_json_model(
        'user1', community_create.json, new_community)


def test_edit_community_name(init_client):
    client, tokens = init_client
    client.post('/api/community/', json={'name': 'test'},
                headers=auth_header(tokens[0]))
    bad_community_edit = client.put(
        '/api/community/1', json={}, headers=auth_header(tokens[0]))
    assert bad_community_edit.status_code == 400

    name_edit = client.put(
        '/api/community/1', json={'new_name': 'works'}, headers=auth_header(tokens[0]))
    assert name_edit.status_code == 200
    assert name_edit.json['name'] == get_community_by_id(
        1).name == 'works'


def test_edit_community_members(init_client):
    client, tokens = init_client
    client.post('/api/community/', json={'name': 'test'},
                headers=auth_header(tokens[0]))

    add_users = client.put('/api/community/1',
                           json={'add_users': ['user2', 'user3']}, headers=auth_header(tokens[0]))
    assert add_users.status_code == 200
    assert len(add_users.json['users']) == len(
        get_community_by_id(1).users) == 3

    name_edit = client.put(
        '/api/community/1', json={'new_name': 'hi'}, headers=auth_header(tokens[0]))
    assert name_edit.status_code == 200
    assert name_edit.json['name'] == get_community_by_id(1).name == 'hi'

    remove_users = client.put('/api/community/1',
                              json={'remove_users': ['user2']}, headers=auth_header(tokens[1]))
    assert remove_users.status_code == 200
    assert len(remove_users.json['users']) == len(
        get_community_by_id(1).users) == 2

    bad_name_edit = client.put(
        '/api/community/1', json={'new_name': 'bye'}, headers=auth_header(tokens[1]))
    assert bad_name_edit.status_code == 403
    assert get_community_by_id(1).name == 'hi'

    fake_name_edit = client.put(
        '/api/community/4', json={'new_name': 'bye'}, headers=auth_header(tokens[1]))
    assert fake_name_edit.status_code == 404


def test_community_info(init_client):
    client, tokens = init_client
    client.post('/api/community/', json={'name': 'happy'},
                headers=auth_header(tokens[0]))
    client.put('/api/community/1',
               json={'add_users': ['user2']}, headers=auth_header(tokens[0]))

    unauthorized_view = client.get(
        '/api/community/1', headers=auth_header(tokens[2]))
    assert unauthorized_view.status_code == 403

    fake_view = client.get(
        '/api/community/5', headers=auth_header(tokens[0]))
    assert fake_view.status_code == 404

    view = client.get('/api/community/1', headers=auth_header(tokens[1]))
    assert view.status_code == 200
    assert view.json['name'] == 'happy'
    assert user_in_community_json_model(
        'user1', view.json, get_community_by_id(1))


def test_community_delete(init_client):
    client, tokens = init_client
    client.post('/api/community/', json={'name': 'deleting'},
                headers=auth_header(tokens[0]))
    client.put('/api/community/1',
               json={'add_users': ['user2']}, headers=auth_header(tokens[0]))

    unauthorized_delete = client.delete(
        '/api/community/1', headers=auth_header(tokens[2]))
    assert unauthorized_delete.status_code == 403

    fake_delete = client.delete(
        '/api/community/2', headers=auth_header(tokens[0]))
    assert fake_delete.status_code == 404

    delete_response = client.delete(
        '/api/community/1', headers=auth_header(tokens[1]))
    assert delete_response.status_code == 204

    removed_view = client.get(
        '/api/community/1', headers=auth_header(tokens[0]))
    assert removed_view.status_code == 404

