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
