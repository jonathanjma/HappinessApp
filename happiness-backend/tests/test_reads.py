import pytest

from api import create_app
from api.app import db
from api.dao.happiness_dao import *
from api.models import User
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
        tokens = [user1.create_token(), user2.create_token(), user3.create_token()]
        db.session.add_all(tokens)
        happiness1 = Happiness(user_id=1, value=8, comment="test1")
        happiness2 = Happiness(user_id=2, value=8, comment="test2")
        happiness3 = Happiness(user_id=3, value=8, comment="test3")
        db.session.add_all([happiness1, happiness2, happiness3])
        db.session.commit()

        yield client, [tokens[0].session_token, tokens[1].session_token, tokens[2].session_token]


def auth_header(token):
    return {'Authorization': f'Bearer {token}'}


header = "/api/"


def test_create_read(init_client):
    client, tokens = init_client
    read1 = client.post(header + "reads", json={
        "user_id": 1,
        "happiness_id": 2,
    })
    assert read1.status_code == 201
