import base64
import string
import random

import pytest

from api import create_app
from api.app import db
from api.users_dao import *
from config import TestConfig
from flask import json

COMPREHENSIVE_TEST = True


@pytest.fixture
def client():
    app = create_app(TestConfig)

    client = app.test_client()
    with app.app_context():
        db.create_all()
        yield client


@pytest.mark.skipif(not COMPREHENSIVE_TEST, reason="Warning: Comprehensive testing is turned off.")
def test_create_user(client):
    """
    Tests the creation of one user. Ensures fields are properly set and response code is correct.
    """
    response = client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'test',
        'password': 'test'
    })
    assert response.status_code == 201
    user = get_user_by_id(1)
    assert user.email == 'test@example.com'
    assert user.username == 'test'


@pytest.mark.skipif(not COMPREHENSIVE_TEST, reason="Warning: Comprehensive testing is turned off.")
def test_create_multiple_users(client):
    """
    Tests the creation of multiple users.
    Ensures that users are properly getting IDs and that making more than one user does not break the application.
    """
    r1 = client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'test',
        'password': 'test',
    })
    r2 = client.post('/api/user/', json={
        'email': 'myemail123@random.com',
        'username': 'john',
        'password': 'doe'
    })
    assert r1.status_code == 201
    assert r2.status_code == 201
    u1 = get_user_by_id(1)
    assert u1.email == 'test@example.com'
    assert u1.username == 'test'
    u2 = get_user_by_id(2)
    assert u2.email == 'myemail123@random.com'
    assert u2.username == 'john'


@pytest.mark.skipif(not COMPREHENSIVE_TEST, reason="Warning: Comprehensive testing is turned off.")
def test_create_invalid_users(client):
    """
    Tests to create invalid users with duplicate emails, usernames, or not enough parameters supplied.
    """
    no_password_res = client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'john'
    })
    assert no_password_res.status_code == 400

    # Create a valid user in order to test invalid users later with identical information
    original_user_res = client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'test',
        'password': 'test',
    })
    assert original_user_res.status_code == 201

    same_email_res = client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'fiddle01',
        'password': 'test',
    })
    assert same_email_res.status_code == 400

    same_username_res = client.post('/api/user/', json={
        'email': 'fiddle01@example.com',
        'username': 'test',
        'password': 'test',
    })
    assert same_username_res.status_code == 400


@pytest.mark.skipif(not COMPREHENSIVE_TEST, reason="Warning: Comprehensive testing is turned off.")
def test_send_invalid_password_reset_email(client):
    """
    Attempts to call send password reset method under invalid conditions.
    Ensures that server does not crash.
    """
    r1 = client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'test',
        'password': 'test',
    })
    # Attempt to post to route with wrong json
    r2 = client.post('/api/user/initiate_password_reset/', json={
        'useless': 'useless@useless.com'
    })
    # Attempt to email a non-existent user
    r3 = client.post('/api/user/initiate_password_reset/', json={
        'email': 'test0@example.com'
    })
    assert r2.status_code == 400
    assert r3.status_code == 404


@pytest.mark.skipif(not COMPREHENSIVE_TEST, reason="Warning: Comprehensive testing is turned off.")
def test_send_password_reset_email(client):
    """
    Tests sending a password reset email to test@example.com
    As long as a success response was returned the email is assumed to have been sent (that's the best we can do)
    """
    r0 = client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'test',
        'password': 'test',
    })
    r1 = client.post('/api/user/', json={
        'email': 'test2@example.com',
        'username': 'test2',
        'password': 'test',
    })
    r2 = client.post('/api/user/initiate_password_reset/', json={
        'email': 'test@example.com'
    })
    r3 = client.post('/api/user/initiate_password_reset/', json={
        'email': 'test2@example.com'
    })
    assert r2.status_code == 200 and r3.status_code == 200


@pytest.mark.skipif(not COMPREHENSIVE_TEST, reason="Warning: Comprehensive testing is turned off.")
def test_login_user(client):
    """
    Tests logging in 2 users and getting their session tokens.
    """
    client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'test',
        'password': 'test',
    })
    client.post('/api/user/', json={
        'email': 'test2@example.com',
        'username': 'test2',
        'password': 'test2',
    })
    user1_credentials = base64.b64encode(b"test:test").decode('utf-8')
    user1_login_res = client.post('/api/token/', headers={"Authorization": f"Basic {user1_credentials}"})
    assert user1_login_res.status_code == 201
    assert json.loads(user1_login_res.get_data()).get("session_token") is not None

    user2_credentials = base64.b64encode(b"test2:test2").decode('utf-8')
    user2_login_res = client.post('/api/token/', headers={"Authorization": f"Basic {user2_credentials}"})
    assert user2_login_res.status_code == 201
    assert json.loads(user2_login_res.get_data()).get("session_token") is not None


@pytest.mark.skipif(not COMPREHENSIVE_TEST, reason="Warning: Comprehensive testing is turned off.")
def test_delete_user(client):
    user_create_response = client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'test',
        'password': 'test',
    })
    user_credentials = base64.b64encode(b"test:test").decode('utf-8')
    assert user_create_response.status_code == 201

    login_response = client.post('/api/token/', headers={"Authorization": f"Basic {user_credentials}"})
    assert login_response.status_code == 201
    bearer_token = json.loads(login_response.get_data()).get("session_token")
    assert bearer_token is not None

    delete_res = client.delete('/api/user/', headers={"Authorization": f"Bearer {bearer_token}"})
    assert delete_res.status_code == 204
    assert (get_user_by_email("text@example.com") is None and get_user_by_username("test") is None
            and get_user_by_id(1) is None)


@pytest.mark.skipif(not COMPREHENSIVE_TEST, reason="Warning: Comprehensive testing is turned off.")
def test_add_user_setting(client):
    """
    Tests adding two settings to a single user in an instance of the backend.
    :param client: The client to perform the test on.
    """
    client, bearer_token = register_and_login_demo_user(client)
    k1, k2 = "SHOW_MEDIAN", "SHOW_MEAN"
    v1, v2 = True, False
    add_median_setting_res = client.post('/api/user/settings/', headers={"Authorization": f"Bearer {bearer_token}"},
                                         json={
                                             "key": k1,
                                             "value": v1
                                         })
    add_mean_setting_res = client.post('/api/user/settings/', headers={"Authorization": f"Bearer {bearer_token}"},
                                       json={
                                           "key": k2,
                                           "value": v2
                                       })
    assert add_median_setting_res.status_code == 201
    assert add_mean_setting_res.status_code == 201

    b1 = json.loads(add_median_setting_res.get_data())
    b2 = json.loads(add_mean_setting_res.get_data())
    assert b1.get("key") == k1
    assert b2.get("key") == k2
    assert b1.get("value") == v1
    assert b2.get("value") == v2
    # Test to make sure the right users get the right setting:
    k3 = "STANDARD_DEVIATION"
    v3 = True
    client, bearer_token2 = register_and_login_demo_user(client)
    add_stdev_setting_res = client.post('/api/user/settings/',
                                        headers={"Authorization": f"Bearer {bearer_token2}"},
                                        json={
                                            "key": k3,
                                            "value": v3
                                        })
    assert add_stdev_setting_res.status_code == 201
    b3 = json.loads(add_stdev_setting_res.get_data())
    assert b3.get("key") == k3
    assert b3.get("value") == v3


# @pytest.mark.skipif(not COMPREHENSIVE_TEST, reason="Warning: Comprehensive testing is turned off.")
def test_get_user_settings(client):
    """
    Tests the get specific user setting and get all user settings operation.
    :param client: The client to perform the test with.
    """
    # Yes this starts the same way as the other test, but unfortunately I don't know how to abstract this.
    # But one day I will be able to write beautiful code hopefully (that is the goal)
    client, bearer_token = register_and_login_demo_user(client)
    k1, k2 = "SHOW_MEDIAN", "SHOW_MEAN"
    v1, v2 = True, False
    add_median_setting_res = client.post('/api/user/settings/', headers={"Authorization": f"Bearer {bearer_token}"},
                                         json={
                                             "key": k1,
                                             "value": v1
                                         })
    add_mean_setting_res = client.post('/api/user/settings/', headers={"Authorization": f"Bearer {bearer_token}"},
                                       json={
                                           "key": k2,
                                           "value": v2
                                       })
    assert add_median_setting_res.status_code == 201
    assert add_mean_setting_res.status_code == 201
    get_settings_res = client.get("/api/user/settings/", headers={"Authorization": f"Bearer {bearer_token}"})
    assert get_settings_res.status_code == 200
    settings = json.loads(get_settings_res.get_data())

    assert settings[0].get("key") == k1
    assert settings[0].get("value") == v1
    assert settings[1].get("key") == k2
    assert settings[1].get("value") == v2


@pytest.mark.skipif(not COMPREHENSIVE_TEST, reason="Warning: Comprehensive testing is turned off.")
def test_change_username(client):
    """
    Tests to change the username of a randomly generated user.
    :param client: The client to perform this action on.
    """
    client, bearer_token = register_and_login_demo_user(client)
    new_username = "Fiddle01"  # Could that name have any meaning associated with it? hmmm
    user_name_change_res = client.post('/api/user/username/', headers={"Authorization": f"Bearer {bearer_token}"}
                                       , json={
            "username": new_username
        })
    assert user_name_change_res.status_code == 200
    assert get_user_by_username(new_username) is not None


@pytest.mark.skipif(not COMPREHENSIVE_TEST, reason="Warning: Comprehensive testing is turned off.")
def test_get_user_by_id(client):
    create_user_res = client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'test',
        'password': 'test',
    })
    assert create_user_res.status_code == 201
    client, bearer_token = register_and_login_demo_user(client, uname_and_password="user2")

    make_group_res = client.post('/api/group/',
                                 json={"name": "Epic group of awesome happiness"},
                                 headers={"Authorization": f"Bearer {bearer_token}"},
                                 )
    add_member_res = client.put('/api/group/1',
                                json={"add_users": ["test"]},
                                headers={"Authorization": f"Bearer {bearer_token}"},
                                )

    assert make_group_res.status_code == 201

    assert add_member_res.status_code == 200

    # Try to get user1's information
    get_user_by_id_res = client.get("/api/user/1", headers={"Authorization": f"Bearer {bearer_token}"})
    # Check that the request went through
    assert get_user_by_id_res.status_code == 200

    # Ensure that the data was as expected
    body_res = json.loads(get_user_by_id_res.get_data())
    assert body_res.get("id") == 1
    assert body_res.get("username") == "test"
    # assert body_res.get("profile_picture") == "default"


@pytest.mark.skipif(not COMPREHENSIVE_TEST, reason="Warning: Comprehensive testing is turned off.")
def test_invalid_get_user_by_id(client):
    create_user_res = client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'test',
        'password': 'test',
    })
    assert create_user_res.status_code == 201
    client, bearer_token = register_and_login_demo_user(client)

    get_initial_user_res = client.get('/api/user/2', headers={"Authorization": f"Bearer {bearer_token}"})
    assert get_initial_user_res.status_code == 403


def random_email():
    """
    Generates a random string with @example.com at the end.
    :return: Random string with @example.com at the end.
    """
    return random_string() + "@example.com"


def random_string():
    """
    Returns a random 10 character string of upper and lowercase letters.
    """
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(10))


def register_and_login_demo_user(client, email=None, uname_and_password=None):
    """
    Creates a demo user for the current client session.
    :param client: The client to connect to for the session.
    :param email: The email of the demo user. Defaults to a random email unless otherwise specified.
    :param uname_and_password: A single string that will be set as both the username and password of the demo user.
    Defaults to a random string unless otherwise specified.
    :return: The client of the current session, followed by the bearer token generated by the login.
    """
    if email is None:
        email = random_email()
    if uname_and_password is None:
        uname_and_password = random_string()
    user_create_response = client.post('/api/user/', json={
        'email': email,
        'username': uname_and_password,
        'password': uname_and_password,
    })

    user_credentials = base64.b64encode((uname_and_password + ":" + uname_and_password).encode()).decode('utf-8')
    assert user_create_response.status_code == 201

    login_response = client.post('/api/token/', headers={"Authorization": f"Basic {user_credentials}"})
    assert login_response.status_code == 201
    bearer_token = json.loads(login_response.get_data()).get("session_token")
    assert bearer_token is not None
    return client, bearer_token
