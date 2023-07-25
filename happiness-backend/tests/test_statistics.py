import random
from datetime import datetime

import pytest
from flask import json

from api import create_app
from api.app import db
from api.dao.users_dao import *
from api.dao.communities_dao import get_community_by_id
from api.dao.statistic_dao import *
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


def test_statistic_create(init_client):
    client, tokens = init_client
    community_response = client.post('/api/community/', json={'name': 'small'},
                                     headers=auth_header(tokens[0]))
    assert community_response.status_code == 201

    statistic_post_1 = client.post('/api/statistic/',
                                   json={'community_id': 1, 'mean': 5, 'median': 4.5, 'stdev': 1, 'minval': 0, 'maxval': 10, 'firstquar': 3.5, 'thirdquar': 6.5, 'timestamp': '2023-06-02'})
    assert statistic_post_1.status_code == 201

    assert statistic_post_1.json['mean'] == get_statistic_by_id(1).mean == 5
    assert statistic_post_1.json['firstquar'] == get_statistic_by_id(
        1).firstquar == 3.5

    duplicate_statistic_post = client.post('/api/statistic/',
                                           json={'community_id': 1, 'mean': 3, 'median': 4.5, 'stdev': 1, 'minval': 0, 'maxval': 10, 'firstquar': 3.5, 'thirdquar': 6.5, 'timestamp': '2023-06-02'})
    assert duplicate_statistic_post.status_code == 400
    assert get_statistic_by_id(1).mean == 5


def test_statistic_edit(init_client):
    client, tokens = init_client
    community_response = client.post('/api/community/', json={'name': 'small'},
                                     headers=auth_header(tokens[0]))
    assert community_response.status_code == 201

    statistic_post_1 = client.post('/api/statistic/',
                                   json={'community_id': 1, 'mean': 5, 'median': 4.5, 'stdev': 1, 'minval': 0, 'maxval': 10, 'firstquar': 3.5, 'thirdquar': 6.5, 'timestamp': '2023-06-02'})
    assert statistic_post_1.status_code == 201

    bad_statistic_edit = client.put(
        '/api/statistic/1', json={'community_id': 1})
    assert bad_statistic_edit.status_code == 400

    good_statistic_edit = client.put(
        '/api/statistic/1', json={'mean': 6.5, 'minval': 0.5})
    assert good_statistic_edit.status_code == 200

    assert good_statistic_edit.json['mean'] == get_statistic_by_id(
        1).mean == 6.5
    assert good_statistic_edit.json['firstquar'] == get_statistic_by_id(
        1).firstquar == 3.5
    assert good_statistic_edit.json['minval'] == get_statistic_by_id(
        1).minval == 0.5


def test_statistic_delete(init_client):
    client, tokens = init_client

    community_response = client.post('/api/community/', json={'name': 'delete'},
                                     headers=auth_header(tokens[0]))
    assert community_response.status_code == 201

    statistic_post_1 = client.post('/api/statistic/',
                                   json={'community_id': 1, 'mean': 5, 'median': 4.5, 'stdev': 1, 'minval': 0, 'maxval': 10, 'firstquar': 3.5, 'thirdquar': 6.5, 'timestamp': '2023-06-02'})
    assert statistic_post_1.status_code == 201

    statistic_delete = client.delete('/api/statistic/1')
    assert statistic_delete.status_code == 204

    bad_statistic_edit = client.put(
        '/api/statistic/1', json={'mean': 6})
    assert bad_statistic_edit.status_code == 404

    empty_statistic_access = client.get('/api/statistic/', query_string={
                                        'start': '2023-06-02', 'community_id': 1}, headers=auth_header(tokens[0]))
    assert empty_statistic_access.status_code == 200
    assert len(empty_statistic_access.json) == 0


def test_stats_date(init_client):
    client, tokens = init_client
    community_response = client.post('/api/community/', json={'name': 'small'},
                                     headers=auth_header(tokens[0]))
    assert community_response.status_code == 201
    assert get_community_by_id(1).name == 'small'

    statistic_post_1 = client.post('/api/statistic/',
                                   json={'community_id': 1, 'mean': 5, 'median': 4.5, 'stdev': 1, 'minval': 0, 'maxval': 10, 'firstquar': 3.5, 'thirdquar': 6.5, 'timestamp': '2023-06-02'}, headers=auth_header(tokens[0]))
    assert statistic_post_1.status_code == 201

    statistic_post_2 = client.post('/api/statistic/',
                                   json={'community_id': 1, 'mean': 6, 'median': 3, 'stdev': 2, 'minval': 1, 'maxval': 8, 'firstquar': 1.5, 'thirdquar': 7, 'timestamp': '2023-06-04'}, headers=auth_header(tokens[0]))
    assert statistic_post_2.status_code == 201

    statistic_post_3 = client.post('/api/statistic/',
                                   json={'community_id': 1, 'mean': 8, 'median': 8, 'stdev': 8, 'minval': 8, 'maxval': 8, 'firstquar': 8, 'thirdquar': 8, 'timestamp': '2023-05-29'}, headers=auth_header(tokens[0]))
    assert statistic_post_3.status_code == 201

    bad_get_statistic = client.get(
        '/api/statistic/', query_string={'end': '2023-05-02'}, headers=auth_header(tokens[0]))
    assert bad_get_statistic.status_code == 400

    unauth_get_statistic = client.get('/api/statistic/', query_string={
                                      'start': '2023-05-01', 'end': '2023-06-02', 'community_id': 1}, headers=auth_header(tokens[1]))
    assert unauth_get_statistic.status_code == 403

    nonexistent_get_statistic = client.get('/api/statistic/', query_string={
                                           'start': '2023-05-10', 'end': '2023-05-31', 'community_id': 2}, headers=auth_header(tokens[0]))
    assert nonexistent_get_statistic.status_code == 404

    good_get_statistic = client.get('/api/statistic/', query_string={
                                    'start': '2023-06-01', 'end': '2023-06-05', 'community_id': 1}, headers=auth_header(tokens[0]))
    assert good_get_statistic.status_code == 200
    assert len(good_get_statistic.json) == 2
    assert good_get_statistic.json[0]['timestamp'] == '2023-06-02'
    assert good_get_statistic.json[0]['mean'] == 5.0
    assert good_get_statistic.json[0]['median'] == 4.5
    assert good_get_statistic.json[0]['stdev'] == 1
    assert good_get_statistic.json[0]['minval'] == 0
    assert good_get_statistic.json[0]['maxval'] == 10.0
    assert good_get_statistic.json[0]['firstquar'] == 3.5
    assert good_get_statistic.json[0]['thirdquar'] == 6.5
    assert good_get_statistic.json[1]['timestamp'] == '2023-06-04'
    assert good_get_statistic.json[1]['mean'] == 6.0
    assert good_get_statistic.json[1]['firstquar'] == 1.5

    no_end_get_statistic = client.get(
        '/api/statistic/', query_string={'start': '2023-05-10', 'community_id': 1}, headers=auth_header(tokens[0]))
    assert no_end_get_statistic.status_code == 200
    assert len(no_end_get_statistic.json) == 3
    # make sure entries in chronological order
    assert no_end_get_statistic.json[0]['timestamp'] == '2023-05-29'
    assert no_end_get_statistic.json[0]['maxval'] == 8.0
    assert no_end_get_statistic.json[2]['timestamp'] == '2023-06-04'


def test_stats_singular_date(init_client):
    client, tokens = init_client
    community_response = client.post('/api/community/', json={'name': 'small2'},
                                     headers=auth_header(tokens[0]))
    assert community_response.status_code == 201
    assert get_community_by_id(1).name == 'small2'

    statistic_post_1 = client.post('/api/statistic/',
                                   json={'community_id': 1, 'mean': 5.25, 'median': 4.5, 'stdev': 1, 'minval': 0, 'maxval': 10, 'firstquar': 3.5, 'thirdquar': 6.5, 'timestamp': '2023-06-02'}, headers=auth_header(tokens[0]))
    assert statistic_post_1.status_code == 201

    empty_get_statistic = client.get('/api/statistic/', query_string={
                                     'start': '2023-06-01', 'end': '2023-06-01', 'community_id': 1}, headers=auth_header(tokens[0]))
    assert empty_get_statistic.status_code == 200
    assert len(empty_get_statistic.json) == 0

    date_get_statistic = client.get('/api/statistic/', query_string={
                                    'start': '2023-06-02', 'end': '2023-06-02', 'community_id': 1}, headers=auth_header(tokens[0]))
    assert date_get_statistic.status_code == 200
    assert len(date_get_statistic.json) == 1
    assert date_get_statistic.json[0]['mean'] == 5.25


def test_stats_dates_multiple_communities(init_client):
    # tests multiple community statistics
    client, tokens = init_client
    community_response = client.post('/api/community/', json={'name': 'big'},
                                     headers=auth_header(tokens[0]))
    assert community_response.status_code == 201
    community_response2 = client.post('/api/community/', json={'name': 'big2'},
                                      headers=auth_header(tokens[1]))
    assert community_response2.status_code == 201
    assert get_community_by_id(1).name == 'big'
    assert get_community_by_id(2).name == 'big2'

    statistic_post_1 = client.post('/api/statistic/',
                                   json={'community_id': 1, 'mean': 5.5, 'median': 4, 'stdev': 1.5, 'minval': 0.5, 'maxval': 9.5, 'firstquar': 3, 'thirdquar': 6, 'timestamp': '2023-06-12'}, headers=auth_header(tokens[0]))
    assert statistic_post_1.status_code == 201

    statistic_post_2 = client.post('/api/statistic/',
                                   json={'community_id': 1, 'mean': 6.5, 'median': 3.5, 'stdev': 2.5, 'minval': 1.5, 'maxval': 8.5, 'firstquar': 2, 'thirdquar': 7.5, 'timestamp': '2023-06-14'}, headers=auth_header(tokens[0]))
    assert statistic_post_2.status_code == 201

    statistic_post_3 = client.post('/api/statistic/',
                                   json={'community_id': 2, 'mean': 8.5, 'median': 8, 'stdev': 8, 'minval': 8, 'maxval': 8, 'firstquar': 8, 'thirdquar': 8, 'timestamp': '2023-06-13'}, headers=auth_header(tokens[1]))
    assert statistic_post_3.status_code == 201

    statistic_post_4 = client.post('/api/statistic/',
                                   json={'community_id': 2, 'mean': 6, 'median': 7, 'stdev': 0.05, 'minval': 1, 'maxval': 8, 'firstquar': 5, 'thirdquar': 7, 'timestamp': '2023-06-15'}, headers=auth_header(tokens[1]))
    assert statistic_post_4.status_code == 201

    statistic_post_5 = client.post('/api/statistic/',
                                   json={'community_id': 1, 'mean': 5, 'median': 5, 'stdev': 0.65, 'minval': 1, 'maxval': 9, 'firstquar': 2, 'thirdquar': 6, 'timestamp': '2023-07-25'}, headers=auth_header(tokens[0]))
    assert statistic_post_5.status_code == 201

    unauth_get_statistic1 = client.get('/api/statistic/', query_string={
                                       'start': '2023-06-02', 'community_id': 2}, headers=auth_header(tokens[0]))
    assert unauth_get_statistic1.status_code == 403

    unauth_get_statistic2 = client.get('/api/statistic/', query_string={
                                       'start': '2023-06-11', 'end': '2023-06-14', 'community_id': 1}, headers=auth_header(tokens[1]))
    assert unauth_get_statistic2.status_code == 403

    get_statistic_community1 = client.get('/api/statistic/', query_string={
        'start': '2023-06-11', 'end': '2023-06-14', 'community_id': 1}, headers=auth_header(tokens[0]))
    assert get_statistic_community1.status_code == 200
    assert len(get_statistic_community1.json) == 2

    add_community_member_response = client.put(
        '/api/community/2', json={'add_users': ['user1']}, headers=auth_header(tokens[1]))
    assert add_community_member_response.status_code == 200

    get_statistic_community2 = client.get('/api/statistic/', query_string={
        'start': '2023-06-11', 'end': '2023-06-14', 'community_id': 2}, headers=auth_header(tokens[0]))
    assert get_statistic_community2.status_code == 200
    assert len(get_statistic_community2.json) == 1

    get_statistic_community3 = client.get('/api/statistic/', query_string={
                                          'start': '2023-05-01', 'community_id': 1}, headers=auth_header(tokens[0]))
    assert get_statistic_community3.status_code == 200
    assert len(get_statistic_community3.json) == 3


def test_stats_count(init_client):
    client, tokens = init_client
    community_response = client.post('/api/community/', json={'name': 'small3'},
                                     headers=auth_header(tokens[0]))
    assert community_response.status_code == 201

    client.post('/api/statistic/', json={'community_id': 1, 'mean': 5, 'median': 4.5, 'stdev': 1, 'minval': 0,
                'maxval': 10, 'firstquar': 3.5, 'thirdquar': 6.5, 'timestamp': '2023-06-02'}, headers=auth_header(tokens[0]))
    client.post('/api/statistic/', json={'community_id': 1, 'mean': 6, 'median': 3, 'stdev': 2, 'minval': 1,
                'maxval': 8, 'firstquar': 1.5, 'thirdquar': 7, 'timestamp': '2023-06-04'}, headers=auth_header(tokens[0]))
    client.post('/api/statistic/', json={'community_id': 1, 'mean': 8, 'median': 8, 'stdev': 8, 'minval': 8,
                'maxval': 8, 'firstquar': 8, 'thirdquar': 8, 'timestamp': '2023-05-29'}, headers=auth_header(tokens[0]))

    good_count_statistic = client.get('/api/statistic/count', query_string={
                                      'page': 1, 'count': 10, 'community_id': 1}, headers=auth_header(tokens[0]))
    assert good_count_statistic.status_code == 200
    assert len(good_count_statistic.json) == 3
