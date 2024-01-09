import base64
import json

import pytest

from api import create_app
from api.dao.groups_dao import get_group_by_id
from api.dao.happiness_dao import *
from api.dao.users_dao import get_user_by_id, get_user_by_username
from api.models.models import User
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


def test_create_happiness_entry(init_client):
    client, tokens = init_client
    happiness_create_response = client.post('/api/happiness/', json={
        'value': 4,
        'comment': 'great day',
        'timestamp': '2023-01-11'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_create_response.status_code == 201
    happiness = get_happiness_by_id(1)
    assert happiness.value == 4
    assert happiness.comment == 'great day'
    assert happiness.timestamp == datetime.strptime('2023-01-11', "%Y-%m-%d")


def test_overwrite_create_happiness_entry(init_client):
    client, tokens = init_client

    happiness_create_response = client.post('/api/happiness/', json={
        'value': 4,
        'comment': 'great day',
        'timestamp': '2023-01-11'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_create_response.status_code == 201

    happiness_create_response_2 = client.post('/api/happiness/', json={
        'value': 8,
        'comment': 'amazing day',
        'timestamp': '2023-01-11'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    happiness = json.loads(happiness_create_response_2.get_data())
    assert happiness_create_response_2.status_code == 201
    assert happiness.get("comment") == "amazing day"
    assert happiness.get("value") == 8

    start_end_response = client.get('/api/happiness/', query_string={
        'start': '2023-01-11',
        'end': '2023-01-11',
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    happiness_list = json.loads(start_end_response.get_data())
    assert start_end_response.status_code == 200
    assert happiness_list[0].get("comment") == "amazing day"
    assert happiness_list[0].get("value") == 8


def test_edit_happiness(init_client):
    client, tokens = init_client
    happiness_create_response = client.post('/api/happiness/', json={
        'value': 4,
        'comment': 'great day',
        'timestamp': '2023-01-11'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_create_response.status_code == 201
    happiness = get_happiness_by_id(1)
    assert happiness.value == 4
    assert happiness.comment == 'great day'
    assert happiness.timestamp == datetime.strptime('2023-01-11', "%Y-%m-%d")

    happiness_create_response2 = client.post('/api/happiness/', json={
        'value': 9,
        'comment': 'bad day',
        'timestamp': '2023-01-12'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_create_response2.status_code == 201
    happiness2 = get_happiness_by_id(2)
    assert happiness2.value == 9
    assert happiness2.comment == 'bad day'
    assert happiness2.timestamp == datetime.strptime('2023-01-12', "%Y-%m-%d")

    happiness_set_response = client.put('/api/happiness/?id=2', json={
        'value': 6,
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_set_response.status_code == 200
    happiness3 = get_happiness_by_id(2)
    assert happiness3.value == 6
    assert happiness3.comment == 'bad day'

    happiness_edit_response = client.put('/api/happiness/?date=2023-01-11', json={
        'comment': 'test'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_edit_response.status_code == 200
    h = get_happiness_by_id(1)
    assert h.value == 4
    assert h.comment == 'test'

    happiness_set_response2 = client.put('/api/happiness/?id=1', json={
        'value': 0.0,
        'comment': 'asdadsadsad',
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_set_response2.status_code == 200
    happiness4 = get_happiness_by_id(1)
    assert happiness4.value == 0.0
    assert happiness4.comment == 'asdadsadsad'


def test_delete_happiness(init_client):
    client, tokens = init_client
    happiness_create_response = client.post('/api/happiness/', json={
        'value': 4,
        'comment': 'great day',
        'timestamp': '2023-01-11'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_create_response.status_code == 201
    happiness_delete_response = client.delete(
        '/api/happiness/?id=1', headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_delete_response.status_code == 204


@pytest.mark.skip(reason="Aaron needs to refactor and fix this test case")
def test_get_happiness(init_client):
    client, tokens = init_client
    client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'test',
        'password': 'test',
    })
    user_credentials = base64.b64encode(b"test:test").decode('utf-8')

    login_response = client.post(
        '/api/token/', headers={"Authorization": f"Basic {user_credentials}"})
    bearer_token = json.loads(login_response.get_data()).get("session_token")

    client.post('/api/happiness/', json={
        'value': 4,
        'comment': 'great day',
        'timestamp': '2023-01-11'
    }, headers={"Authorization": f"Bearer {bearer_token}"})

    client.post('/api/happiness/', json={
        'value': 9,
        'comment': 'bad day',
        'timestamp': '2023-01-12'
    }, headers={"Authorization": f"Bearer {bearer_token}"})

    client.post('/api/happiness/', json={
        'value': 3,
        'comment': 'very happy',
        'timestamp': '2023-01-13'
    }, headers={"Authorization": f"Bearer {bearer_token}"})

    client.post('/api/happiness/', json={
        'value': 6.5,
        'comment': 'hmmm',
        'timestamp': '2023-01-14'
    }, headers={"Authorization": f"Bearer {bearer_token}"})

    client.post('/api/happiness/', json={
        'value': 7.5,
        'comment': 'oopsies',
        'timestamp': '2023-01-16'
    }, headers={"Authorization": f"Bearer {bearer_token}"})

    client.post('/api/happiness/', json={
        'value': 9.5,
        'comment': 'happiest',
        'timestamp': '2023-01-29'
    }, headers={"Authorization": f"Bearer {bearer_token}"})

    client.post('/api/happiness/', json={
        'value': 3,
        'comment': 'no',
        'timestamp': '2023-01-14'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})

    start_end_response = client.get('/api/happiness/', query_string={
        'start': '2023-01-03',
        'end': '2023-01-13',
    }, headers={"Authorization": f"Bearer {bearer_token}"})
    assert start_end_response.json == [
        {'comment': 'great day', 'id': 1,
         'timestamp': '2023-01-11', 'user_id': 4, 'value': 4.0},
        {'comment': 'bad day', 'id': 2, 'timestamp': '2023-01-12',
         'user_id': 4, 'value': 9.0},
        {'comment': 'very happy', 'id': 3,
         'timestamp': '2023-01-13', 'user_id': 4, 'value': 3.0}
    ]
    assert start_end_response.status_code == 200

    start_only_response = client.get('/api/happiness/', query_string={
        'start': '2023-01-13',
        'id': 4,
    }, headers={"Authorization": f"Bearer {bearer_token}"})
    assert start_only_response.status_code == 200
    assert start_only_response.json == [
        {'comment': 'very happy', 'id': 3,
         'timestamp': '2023-01-13', 'user_id': 4, 'value': 3.0},
        {'comment': 'hmmm', 'id': 4, 'timestamp': '2023-01-14',
         'user_id': 4, 'value': 6.5},
        {'comment': 'oopsies', 'id': 5, 'timestamp': '2023-01-16',
         'user_id': 4, 'value': 7.5},
        {'comment': 'happiest', 'id': 6,
         'timestamp': '2023-01-29', 'user_id': 4, 'value': 9.5}]

    happiness_get_response3 = client.get('/api/happiness/', json={
    }, headers={"Authorization": f"Bearer {bearer_token}"})
    print("ok")
    print(happiness_get_response3.json)
    assert happiness_get_response3.json == [
        {'comment': 'great day', 'id': 1,
         'timestamp': '2023-01-11', 'user_id': 4, 'value': 4.0},
        {'comment': 'bad day', 'id': 2, 'timestamp': '2023-01-12',
         'user_id': 4, 'value': 9.0},
        {'comment': 'very happy', 'id': 3,
         'timestamp': '2023-01-13', 'user_id': 4, 'value': 3.0},
        {'comment': 'hmmm', 'id': 4, 'timestamp': '2023-01-14',
         'user_id': 4, 'value': 6.5},
        {'comment': 'oopsies', 'id': 5, 'timestamp': '2023-01-16',
         'user_id': 4, 'value': 7.5},
        {'comment': 'happiest', 'id': 6,
         'timestamp': '2023-01-29', 'user_id': 4, 'value': 9.5}]
    assert happiness_get_response3.status_code == 200

    bad_happiness_get_other_response = client.get('/api/happiness/', query_string={
        'start': '2023-01-02',
        'end': '2023-01-30',
        'id': 1
    }, headers={"Authorization": f"Bearer {bearer_token}"})
    assert bad_happiness_get_other_response.status_code == 403

    bd = client.post('/api/group/', json={'name': 'test'},
                     headers={"Authorization": f"Bearer {tokens[0]}"})
    assert bd.status_code == 201
    bda = client.put('/api/group/1', json={
        'invite_users': ['user2', 'test']
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert bda.status_code == 200

    bdacc1 = client.post('/api/user/accept_invite/1',
                         headers={"Authorization": f"Bearer {tokens[1]}"})
    bdacc2 = client.post('/api/user/accept_invite/1',
                         headers={"Authorization": f"Bearer {bearer_token}"})
    assert bdacc1.status_code == 204 and bdacc2.status_code == 204

    my_user_obj = get_user_by_id(1)
    id = 4
    assert my_user_obj.has_mutual_group(get_user_by_id(id))

    happiness_get_other_response = client.get('/api/happiness/', query_string={
        'start': '2023-01-02',
        'end': '2023-01-30',
        'id': 1
    }, headers={"Authorization": f"Bearer {bearer_token}"})
    assert happiness_get_other_response.status_code == 200
    assert happiness_get_other_response.json == [{
        'comment': 'no',
        'id': 7,
        'timestamp': '2023-01-14',
        'user_id': 1,
        'value': 3.0
    }]

    happiness_get_count_response = client.get('/api/happiness/count', query_string={
        'count': 5,
        'id': 4,
    }, headers={"Authorization": f"Bearer {tokens[1]}"})
    assert happiness_get_count_response.status_code == 200
    assert happiness_get_count_response.json == [
        {'comment': 'happiest', 'id': 6,
         'timestamp': '2023-01-29', 'user_id': 4, 'value': 9.5},
        {'comment': 'oopsies', 'id': 5, 'timestamp': '2023-01-16',
         'user_id': 4, 'value': 7.5},
        {'comment': 'hmmm', 'id': 4, 'timestamp': '2023-01-14',
         'user_id': 4, 'value': 6.5},
        {'comment': 'very happy', 'id': 3,
         'timestamp': '2023-01-13', 'user_id': 4, 'value': 3.0},
        {'comment': 'bad day', 'id': 2, 'timestamp': '2023-01-12',
         'user_id': 4, 'value': 9.0},
    ]

    happiness_get_count_response2 = client.get('/api/happiness/count',
                                               headers={"Authorization": f"Bearer {bearer_token}"})
    assert happiness_get_count_response2.status_code == 200
    assert happiness_get_count_response2.json == [
        {'comment': 'happiest', 'id': 6,
         'timestamp': '2023-01-29', 'user_id': 4, 'value': 9.5},
        {'comment': 'oopsies', 'id': 5, 'timestamp': '2023-01-16',
         'user_id': 4, 'value': 7.5},
        {'comment': 'hmmm', 'id': 4, 'timestamp': '2023-01-14',
         'user_id': 4, 'value': 6.5},
        {'comment': 'very happy', 'id': 3,
         'timestamp': '2023-01-13', 'user_id': 4, 'value': 3.0},
        {'comment': 'bad day', 'id': 2, 'timestamp': '2023-01-12',
         'user_id': 4, 'value': 9.0},
        {'comment': 'great day', 'id': 1,
         'timestamp': '2023-01-11', 'user_id': 4, 'value': 4.0},
    ]

    happiness_get_count_response3 = client.get('/api/happiness/count', query_string={
        'count': 3,
        'page': 2,
        'id': 4
    }, headers={"Authorization": f"Bearer {bearer_token}"})
    assert happiness_get_count_response3.status_code == 200
    assert happiness_get_count_response3.json == [
        {'comment': 'very happy', 'id': 3,
         'timestamp': '2023-01-13', 'user_id': 4, 'value': 3.0},
        {'comment': 'bad day', 'id': 2, 'timestamp': '2023-01-12',
         'user_id': 4, 'value': 9.0},
        {'comment': 'great day', 'id': 1,
         'timestamp': '2023-01-11', 'user_id': 4, 'value': 4.0},
    ]

    happiness_get_count_response4 = client.get('/api/happiness/count', query_string={
        'count': 10,
        'page': 2,
        'id': 4
    }, headers={"Authorization": f"Bearer {bearer_token}"})
    assert happiness_get_count_response4.status_code == 200
    assert happiness_get_count_response4.json == []

    bad_happiness_get_count = client.get('/api/happiness/count', query_string={
        'count': 3,
        'page': 2,
        'id': 4
    }, headers={"Authorization": f"Bearer {tokens[2]}"})
    assert bad_happiness_get_count.status_code == 403


def test_discussion_comments_create(init_client):
    client, tokens = init_client
    client.post('/api/group/', json={'name': 'group 1'}, headers=auth_header(tokens[0]))
    client.post('/api/group/', json={'name': 'group 2'}, headers=auth_header(tokens[0]))
    client.post('/api/happiness/', json={
        'value': 4.5,
        'comment': 'bad day',
        'timestamp': '2023-06-19'
    }, headers=auth_header(tokens[0]))

    unauthorized_comment = client.post('/api/happiness/1/comment', json={
        'text': 'rip'
    }, headers=auth_header(tokens[1]))
    assert unauthorized_comment.status_code == 403

    get_group_by_id(1).invite_users(['user2'])
    get_group_by_id(1).add_user(get_user_by_username('user2'))
    get_group_by_id(2).invite_users(['user3'])
    get_group_by_id(2).add_user(get_user_by_username('user3'))

    create_comment = client.post('/api/happiness/1/comment', json={
        'text': 'oh no what happened?'
    }, headers=auth_header(tokens[1]))
    create_comment2 = client.post('/api/happiness/1/comment', json={
        'text': 'i messed up bad'
    }, headers=auth_header(tokens[0]))
    create_comment3 = client.post('/api/happiness/1/comment', json={
        'text': 'is it related to your mom?'
    }, headers=auth_header(tokens[2]))
    assert create_comment.status_code == 201
    assert create_comment2.status_code == 201
    assert create_comment3.status_code == 201

    get_comments = client.get('/api/happiness/1/comments', query_string={
        'start': '2023-06-19'
    }, headers=auth_header(tokens[0]))
    comments = get_comments.json
    assert len(comments) == 3
    assert comments[0]['happiness_id'] == comments[1]['happiness_id'] == 1
    assert comments[0]['author']['id'] == 2 and comments[1]['author']['id'] == 1
    assert comments[0]['text'] == 'oh no what happened?' and comments[1]['text'] == 'i messed up bad'

    comment_access_u2 = client.get('/api/happiness/1/comments', query_string={
        'start': '2023-06-19'
    }, headers=auth_header(tokens[1]))
    comments = comment_access_u2.json
    assert len(comments) == 2
    assert comments[0]['author']['id'] == 2 and comments[1]['author']['id'] == 1

    comment_access_u3 = client.get('/api/happiness/1/comments', query_string={
        'start': '2023-06-19'
    }, headers=auth_header(tokens[2]))
    comments = comment_access_u3.json
    assert len(comments) == 2
    assert comments[0]['author']['id'] == 1 and comments[1]['author']['id'] == 3


def test_happiness_search(init_client):
    client, tokens = init_client
    init_test_data(client, tokens)

    happiness_number_range_3_4 = client.get('api/happiness/search', query_string={
        'low': 3,
        'high': 4,
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_number_range_3_4.status_code == 200
    assert (list(map(lambda d: d.get("comment"), happiness_number_range_3_4.json)) == ['no', 'very happy', 'great day'])

    happiness_number_range_6pt5_9pt5 = client.get('api/happiness/search', query_string={
        'low': 6.5,
        'high': 9.5,
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_number_range_6pt5_9pt5.status_code == 200
    assert (list(map(lambda d: d.get("comment"), happiness_number_range_6pt5_9pt5.json)) == ['happiest', 'oopsies',
                                                                                             'hmmm', 'bad day'])

    happiness_date_range_12_14 = client.get('api/happiness/search', query_string={
        'start': '2023-01-12',
        'end': '2023-01-14',
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_date_range_12_14.status_code == 200
    assert (list(map(lambda d: d.get("comment"), happiness_date_range_12_14.json)) == ['hmmm', 'very happy', 'bad day'])

    happiness_text_day = client.get('api/happiness/search', query_string={
        'text': 'day',
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_text_day.status_code == 200
    assert (list(map(lambda d: d.get("comment"), happiness_text_day.json)) == ['bad day', 'great day'])

    happiness_text_casesensitivity_happiest = client.get('api/happiness/search', query_string={
        'text': 'haPpIEsT',
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_text_casesensitivity_happiest.status_code == 200
    assert (list(map(lambda d: d.get("comment"), happiness_text_casesensitivity_happiest.json)) == ['happiest'])

    happiness_number_range_3_4_date_range_12_14_very = client.get('api/happiness/search', query_string={
        'low': 3,
        'high': 7,
        'start': '2023-01-12',
        'end': '2023-01-14',
        'text': 'very',
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_number_range_3_4_date_range_12_14_very.status_code == 200
    assert (list(map(lambda d: d.get("comment"), happiness_number_range_3_4_date_range_12_14_very.json)) ==
            ['very happy'])

    happiness_date_range_16_29_number_range_8_10 = client.get('api/happiness/search', query_string={
        'low': 8,
        'high': 10,
        'start': '2023-01-16',
        'end': '2023-01-29',
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_date_range_16_29_number_range_8_10.status_code == 200
    assert (list(map(lambda d: d.get("comment"), happiness_date_range_16_29_number_range_8_10.json)) == ['happiest'])

    happiness_date_range_11_14_day = client.get('api/happiness/search', query_string={
        'start': '2023-01-11',
        'end': '2023-01-14',
        'text': 'day',
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_date_range_11_14_day.status_code == 200
    assert (list(map(lambda d: d.get("comment"), happiness_date_range_11_14_day.json)) == ['bad day', 'great day'])

    happiness_number_range_5_10_hmmm = client.get('api/happiness/search', query_string={
        'low': 5,
        'high': 10,
        'text': "hmmm",
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_number_range_5_10_hmmm.status_code == 200
    assert (list(map(lambda d: d.get("comment"), happiness_number_range_5_10_hmmm.json)) == ['hmmm'])

    happiness_empty = client.get('api/happiness/search', query_string={
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_empty.status_code == 200
    assert (list(map(lambda d: d.get("comment"), happiness_empty.json)) == [])

    happiness_number_range_9_9 = client.get('api/happiness/search', query_string={
        'low': 9,
        'high': 9,
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_number_range_9_9.status_code == 200
    assert (list(map(lambda d: d.get("comment"), happiness_number_range_9_9.json)) == ['bad day'])

    happiness_number_range_10_5_hmmm = client.get('api/happiness/search', query_string={
        'low': 10,
        'high': 5,
        'text': "hmmm",
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_number_range_10_5_hmmm.status_code == 400

    happiness_date_range_14_11_day = client.get('api/happiness/search', query_string={
        'start': '2023-01-14',
        'end': '2023-01-11',
        'text': 'day',
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_date_range_14_11_day.status_code == 400


def test_happiness_count(init_client):
    client, tokens = init_client
    init_test_data(client, tokens)
    happiness_number_range_3_4 = client.get('api/happiness/search/count', query_string={
        'low': 3,
        'high': 4,
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_number_range_3_4.status_code == 200
    assert happiness_number_range_3_4.json['number'] == 3

    happiness_text_day = client.get('api/happiness/search/count', query_string={
        'text': 'day',
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_text_day.status_code == 200
    assert happiness_text_day.json['number'] == 2


def test_happiness_count_0(init_client):
    client, tokens = init_client
    init_test_data(client, tokens)
    empty_1 = client.get('api/happiness/search/count', headers={"Authorization": f"Bearer {tokens[0]}"})
    assert empty_1.status_code == 200
    assert empty_1.json['number'] == 0

    empty_2 = client.get('api/happiness/search/count', query_string={
        'start': '2023-02-01',
        'end': '2023-02-27'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert empty_2.status_code == 200
    assert empty_2.json['number'] == 0


def init_test_data(client, tokens):
    client.post('/api/happiness/', json={
        'value': 4,
        'comment': 'great day',
        'timestamp': '2023-01-11'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})

    client.post('/api/happiness/', json={
        'value': 9,
        'comment': 'bad day',
        'timestamp': '2023-01-12'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})

    client.post('/api/happiness/', json={
        'value': 3,
        'comment': 'very happy',
        'timestamp': '2023-01-13'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})

    client.post('/api/happiness/', json={
        'value': 6.5,
        'comment': 'hmmm',
        'timestamp': '2023-01-14'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})

    client.post('/api/happiness/', json={
        'value': 7.5,
        'comment': 'oopsies',
        'timestamp': '2023-01-16'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})

    client.post('/api/happiness/', json={
        'value': 9.5,
        'comment': 'happiest',
        'timestamp': '2023-01-29'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})

    client.post('/api/happiness/', json={
        'value': 3,
        'comment': 'no',
        'timestamp': '2023-01-15'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})


def test_discussion_comments_edit(init_client):
    client, tokens = init_client
    client.post('/api/group/', json={'name': 'group 1'}, headers=auth_header(tokens[0]))
    get_group_by_id(1).invite_users(['user2'])
    get_group_by_id(1).add_user(get_user_by_username('user2'))
    client.post('/api/happiness/', json={
        'value': 4.5,
        'comment': 'bad day',
        'timestamp': '2023-06-19'
    }, headers=auth_header(tokens[0]))
    client.post('/api/happiness/1/comment', json={
        'text': 'oh no what happened?'
    }, headers=auth_header(tokens[1]))
    client.post('/api/happiness/1/comment', json={
        'text': 'call tonight?'
    }, headers=auth_header(tokens[1]))

    bad_edit1 = client.put('/api/happiness/comments/5', json={
        'data': 'are you feeling ok?'
    }, headers=auth_header(tokens[0]))
    assert bad_edit1.status_code == 404

    bad_edit2 = client.put('/api/happiness/comments/1', json={
        'data': 'are you feeling ok?'
    }, headers=auth_header(tokens[0]))
    assert bad_edit2.status_code == 403

    edit = client.put('/api/happiness/comments/1', json={
        'data': 'are you feeling ok?'
    }, headers=auth_header(tokens[1]))
    assert edit.status_code == 200

    get_comments = client.get('/api/happiness/1/comments', query_string={
        'start': '2023-06-19'
    }, headers=auth_header(tokens[0]))
    assert get_comments.json[0]['text'] == 'are you feeling ok?'


def test_discussion_comments_delete(init_client):
    client, tokens = init_client
    client.post('/api/group/', json={'name': 'group 1'}, headers=auth_header(tokens[0]))
    get_group_by_id(1).invite_users(['user2'])
    get_group_by_id(1).add_user(get_user_by_username('user2'))
    client.post('/api/happiness/', json={
        'value': 4.5,
        'comment': 'bad day',
        'timestamp': '2023-06-19'
    }, headers=auth_header(tokens[0]))
    client.post('/api/happiness/1/comment', json={
        'text': 'oh no what happened?'
    }, headers=auth_header(tokens[1]))
    client.post('/api/happiness/1/comment', json={
        'text': 'call tonight?'
    }, headers=auth_header(tokens[1]))

    bad_delete = client.delete('/api/happiness/comments/1', headers=auth_header(tokens[0]))
    assert bad_delete.status_code == 403

    delete = client.delete('/api/happiness/comments/1', headers=auth_header(tokens[1]))
    assert delete.status_code == 204

    get_comments = client.get('/api/happiness/1/comments', query_string={
        'start': '2023-06-19'
    }, headers=auth_header(tokens[0]))
    assert get_comments.json[0]['text'] == 'call tonight?'
