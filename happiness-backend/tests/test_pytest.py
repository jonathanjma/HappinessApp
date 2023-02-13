import pytest

from api import create_app
from api.app import db
from api.users_dao import *
from api.happiness_dao import *
from config import TestConfig
import json
import base64


@pytest.fixture
def client():
    app = create_app(TestConfig)

    client = app.test_client()
    with app.app_context():
        db.create_all()
        yield client


def test_create_user(client):
    response = client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'test',
        'password': 'test'
    })
    assert response.status_code == 201
    user = get_user_by_id(1)

    assert user.email == 'test@example.com'
    assert user.username == 'test'


def test_delete_user(client):
    user_create_response = client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'test',
        'password': 'test',
    })
    user_credentials = base64.b64encode(b"test:test").decode('utf-8')
    assert user_create_response.status_code == 201

    login_response = client.post(
        '/api/token/', headers={"Authorization": f"Basic {user_credentials}"})
    assert login_response.status_code == 200
    bearer_token = json.loads(login_response.get_data()).get("session_token")
    assert bearer_token is not None

    delete_res = client.delete(
        '/api/user/', headers={"Authorization": f"Bearer {bearer_token}"})
    assert delete_res.status_code == 200
    assert (get_user_by_email("text@example.com") is None and get_user_by_username("test") is None
            and get_user_by_id(1) is None)


def test_create_happiness(client):
    user_making = client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'test',
        'password': 'test'
    })
    assert user_making.status_code == 201
    # figure out how to do authentication
    response = client.post('/api/happiness', json={
        'value': 4,
        'comment': 'great day',
        'timestamp': '2023-01-11'
    })
    assert response.status_code == 201
    happiness = get_happiness_by_id(1)
    assert happiness.value == 4
    assert happiness.comment == 'great day'
    assert happiness.timestamp == '2023-01-11'
