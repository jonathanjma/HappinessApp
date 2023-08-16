import datetime
import json

import pytest

from api import create_app
from api.app import db
from api.dao.happiness_dao import *
from api.models.models import User, Group
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
        db.session.commit()
        minus1hr = datetime.datetime.utcnow() - datetime.timedelta(hours=1)

        add_happiness(minus1hr)

        yield client, [tokens[0].session_token, tokens[1].session_token, tokens[2].session_token]


def auth_header(token):
    return {'Authorization': f'Bearer {token}'}


url = "api/reads/"


def auth_header(token):
    return {
        'Authorization': f'Bearer {token}'
    }


def test_create_read(init_client):
    client, tokens = init_client
    read1 = client.post(url, json={
        "happiness_id": 2,
    }, headers=auth_header(tokens[0]))
    assert read1.status_code == 201
    return init_client


def test_invalid_delete_read(init_client):
    client, tokens = init_client
    # try removing before it exists
    delete1 = client.delete(url, json={
        "happiness_id": 2
    }, headers=auth_header(tokens[0]))
    assert delete1.status_code == 400


def test_valid_delete_read(init_client):
    client, tokens = test_create_read(init_client)
    delete1 = client.delete(url, json={
        "happiness_id": 2
    }, headers=auth_header(tokens[0]))
    assert delete1.status_code == 200


def test_get_read_happiness(init_client):
    client, tokens = test_create_read(init_client)
    read2 = client.post(url, json={
        "happiness_id": 1,
    }, headers=auth_header(tokens[0]))
    assert read2.status_code == 201

    get1 = client.get(url, headers=auth_header(tokens[0]))
    assert get1.status_code == 200

    happiness_list = json.loads(get1.get_data())
    assert len(happiness_list) == 2
    assert all([h.get("id") == 1 or 2 for h in happiness_list])


def test_get_empty_read_happiness(init_client):
    client, tokens = init_client
    get1 = client.get(url, headers=auth_header(tokens[0]))
    assert get1.status_code == 200
    happiness_list = json.loads(get1.get_data())
    assert len(happiness_list) == 0


def test_get_unread_happiness(init_client):
    add_group()

    client, tokens = test_create_read(init_client)
    get1 = client.get(url + "unread/", headers=auth_header(tokens[0]))
    assert get1.status_code == 200
    happiness_list = json.loads(get1.get_data())
    assert len(happiness_list) == 2
    assert all([h.get("id") != 2 for h in happiness_list])


def test_get_empty_unread_happiness_1(init_client):
    # should be empty because the user doesn't share any groups with other users
    client, tokens = test_create_read(init_client)
    get1 = client.get(url + "unread/", headers=auth_header(tokens[0]))
    assert get1.status_code == 200
    happiness_list = json.loads(get1.get_data())
    assert len(happiness_list) == 0


def test_get_empty_unread_happiness_2(init_client):
    client, tokens = test_create_read(init_client)
    # should be empty because all happiness is outdated and no longer relevant
    db.session.query(Happiness).delete()
    db.session.commit()
    minus2weeks = datetime.datetime.utcnow() - datetime.timedelta(weeks=2)
    add_happiness(minus2weeks)
    add_group()
    get = client.get(url + "unread/", headers=auth_header(tokens[0]))
    assert get.status_code == 200
    happiness_list = json.loads(get.get_data())
    assert len(happiness_list) == 0


def test_get_empty_unread_happiness_3(init_client):
    client, tokens = test_create_read(init_client)
    # should be empty if user reads all happiness entries
    user1 = (db.session.query(User).first())
    all_happiness = db.session.query(Happiness).all()
    for h in all_happiness:
        user1.read_happiness(h)
    db.session.commit()
    add_group()
    get = client.get(url + "unread/", headers=auth_header(tokens[0]))
    assert get.status_code == 200
    happiness_list = json.loads(get.get_data())
    assert len(happiness_list) == 0


def add_group():
    group1 = Group(name="special test")
    group1.add_users(["user1", "user2", "user3"])
    db.session.add(group1)
    db.session.commit()


def add_happiness(timestamp):
    happiness1 = Happiness(user_id=1, value=8, comment="test1", timestamp=timestamp)
    happiness2 = Happiness(user_id=2, value=8, comment="test2", timestamp=timestamp)
    happiness3 = Happiness(user_id=3, value=8, comment="test3", timestamp=timestamp)
    db.session.add_all([happiness1, happiness2, happiness3])
    db.session.commit()
