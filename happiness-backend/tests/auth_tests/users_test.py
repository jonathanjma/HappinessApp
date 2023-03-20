import pytest
from api import create_app
from api.app import db
from api.users_dao import *
from config import TestConfig


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
