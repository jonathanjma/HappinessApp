import base64
import random
import string

import pytest
from flask import json
from sqlalchemy.sql.functions import current_user

from api import create_app
from api.app import db
from api.dao.groups_dao import get_group_by_id
from api.dao.users_dao import *
from api.models.models import Happiness
from config import TestConfig
from tests.test_groups import auth_header, invite_in_group_json_model, group_in_user_modal, invite_in_user_modal, \
    user_in_group_json_model


@pytest.fixture
def client():
    app = create_app(TestConfig)

    client = app.test_client()
    with app.app_context():
        db.create_all()
        yield client


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
    assert r2.status_code == 400 and r3.status_code == 400


def test_send_password_reset_email(client):
    """
    Tests sending a password reset email to test@example.com
    As long as a success response was returned the email is assumed to have been sent (that's the best we can do)
    """
    client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'test',
        'password': 'test',
    })
    r2 = client.post('/api/user/initiate_password_reset/', json={
        'email': 'test@example.com'
    })
    r3 = client.post('/api/user/initiate_password_reset/', json={
        'email': 'test2@example.com'
    })
    assert r2.status_code == 204 and r3.status_code == 400


def test_reset_password(client):
    client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'test',
        'password': 'test',
    })
    user = get_user_by_id(1)

    bad_reset = client.post('/api/user/reset_password/' + 'reset_token',
                            json={'password': 'W password'})
    assert bad_reset.status_code == 400

    reset_token = user.generate_password_reset_token()
    reset_password = client.post('/api/user/reset_password/' + reset_token,
                                 json={'password': 'W password'})
    assert reset_password.status_code == 204

    user_credentials = base64.b64encode("test:W password".encode()).decode('utf-8')
    login_response = client.post(
        '/api/token/', headers={"Authorization": f"Basic {user_credentials}"})
    assert login_response.status_code == 201

    reset_token2 = user.generate_password_reset_token(0)
    reset_password2 = client.post('/api/user/reset_password/' + reset_token2,
                                 json={'password': 'bad password'})
    assert reset_password2.status_code == 400

    user_credentials2 = base64.b64encode("test:bad password".encode()).decode('utf-8')
    login_response2 = client.post(
        '/api/token/', headers={"Authorization": f"Basic {user_credentials2}"})
    assert login_response2.status_code == 401


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

    user1_credentials2 = base64.b64encode(
        b"test@example.com:test").decode('utf-8')
    user1_login_res2 = client.post(
        '/api/token/', headers={"Authorization": f"Basic {user1_credentials2}"})
    assert user1_login_res2.status_code == 201
    assert json.loads(user1_login_res2.get_data()).get(
        "session_token") is not None

    user1_credentials2 = base64.b64encode(
        b"test@example.com:test").decode('utf-8')
    user1_login_res2 = client.post(
        '/api/token/', headers={"Authorization": f"Basic {user1_credentials2}"})
    assert user1_login_res2.status_code == 201
    assert json.loads(user1_login_res2.get_data()).get(
        "session_token") is not None

    user2_credentials = base64.b64encode(b"test2:test2").decode('utf-8')
    user2_login_res = client.post(
        '/api/token/', headers={"Authorization": f"Basic {user2_credentials}"})
    assert user2_login_res.status_code == 201
    assert json.loads(user2_login_res.get_data()).get(
        "session_token") is not None


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
    assert login_response.status_code == 201
    bearer_token = json.loads(login_response.get_data()).get("session_token")
    assert bearer_token is not None

    delete_res = client.delete('/api/user/', json={
            'password': 'test',
        }, headers={"Authorization": f"Bearer {bearer_token}"})
    assert delete_res.status_code == 204
    assert (get_user_by_email("text@example.com") is None and get_user_by_username("test") is None
            and get_user_by_id(1) is None)


def test_delete_user_2(init_client):
    client, tokens = init_client
    init_test_data(client, tokens)
    assert (get_user_by_email("test1@example.app") is not None and get_user_by_username("user1") is not None and
            get_user_by_id(1) is not None)

    # having user make happiness entry

    happiness_create_response0 = client.post('/api/happiness/', json={
        'value': 2,
        'comment': 'not great day',
        'timestamp': '2024-01-11'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_create_response0.status_code == 201

    # creating a big group

    client.post('/api/group/', json={'name': 'test'}, headers=auth_header(tokens[0]))

    invite_users = client.put('/api/group/1', json={
        'invite_users': ['user2', 'user3']
    }, headers=auth_header(tokens[0]))
    assert invite_users.status_code == 200
    assert len(invite_users.json['invited_users']) == len(get_group_by_id(1).invited_users) == 2
    assert invite_in_group_json_model('user2', invite_users.json, get_group_by_id(1))
    assert invite_in_group_json_model('user3', invite_users.json, get_group_by_id(1))
    assert not group_in_user_modal(1, get_user_by_id(2))
    assert invite_in_user_modal(1, get_user_by_id(2))

    unauthorized_edit = client.put('/api/group/1', json={'name': 'sus'},
                                   headers=auth_header(tokens[1]))
    assert unauthorized_edit.status_code == 403

    bad_accept_invite = client.post('/api/group/accept_invite/5', headers=auth_header(tokens[1]))
    assert bad_accept_invite.status_code == 404

    accept_invite = client.post('/api/group/accept_invite/1', headers=auth_header(tokens[1]))
    assert accept_invite.status_code == 204
    get_group = client.get('/api/group/1', headers=auth_header(tokens[1]))
    assert user_in_group_json_model('user2', get_group.json, get_group_by_id(1))
    assert group_in_user_modal(1, get_user_by_id(2))

    # deleting random member of group

    assert (get_user_by_email("test3@example.app") is not None and get_user_by_username("user3") is not None
            and get_user_by_id(3) is not None)

    delete_res = client.delete(
        '/api/user/', json={
            'password': 'test',
        }, headers={"Authorization": f"Bearer {tokens[2]}"})
    assert delete_res.status_code == 204
    assert (get_user_by_email("test3@example.app") is None and get_user_by_username("user3") is None
            and get_user_by_id(3) is None)

    # deleting creator of group

    delete_res = client.delete(
        '/api/user/', json={
            'password': 'test',
        }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert delete_res.status_code == 204
    assert (get_user_by_email("test1@example.app") is None and get_user_by_username("user1") is None
                and get_user_by_id(1) is None)

    # dealing with a different user, who makes entries and has their own group

    assert (get_user_by_email("test2@example.app") is not None and get_user_by_username("user2") is not None and
            get_user_by_id(2) is not None)

    count_group11 = client.get('/api/user/count/', query_string={
    }, headers=auth_header(tokens[1]))
    assert count_group11.status_code == 200
    assert count_group11.json.get("groups") == 1

    group_create = client.post('/api/group/', json={'name': 'test2'}, headers=auth_header(tokens[1]))
    assert group_create.status_code == 201

    count_group11 = client.get('/api/user/count/', query_string={
    }, headers=auth_header(tokens[1]))
    assert count_group11.status_code == 200
    assert count_group11.json.get("groups") == 2
    assert count_group11.json.get("entries") == 0

    #count numb of happiness entries of user 2 in the database (before making happiness entry)

    happiness_records = db.session.query(Happiness).filter_by(user_id=2).all()
    assert len(happiness_records) == 0

    happiness_create_response0 = client.post('/api/happiness/', json={
        'value': 3,
        'comment': 'not great day',
        'timestamp': '2024-01-11'
    }, headers={"Authorization": f"Bearer {tokens[1]}"})
    assert happiness_create_response0.status_code == 201

    count_group12 = client.get('/api/user/count/', query_string={
    }, headers=auth_header(tokens[1]))
    assert count_group12.status_code == 200
    assert count_group12.json.get("entries") == 1

    # count numb of happiness entries of user 2 in the database (after making happiness entry)

    happiness_records2 = db.session.query(Happiness).filter_by(user_id=2).all()
    assert len(happiness_records2) == 1

    delete_res = client.delete(
        '/api/user/', json={
            'password': 'test',
        }, headers={"Authorization": f"Bearer {tokens[1]}"})
    assert delete_res.status_code == 204
    assert (get_user_by_email("test2@example.app") is None and get_user_by_username("user2") is None
            and get_user_by_id(2) is None)

    # count numb of happiness entries of user 2 in the database (after deleting account)

    happiness_records3 = db.session.query(Happiness).filter_by(user_id=2).all()
    assert len(happiness_records3) == 0


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
                                             "enabled": v1
                                         })
    add_mean_setting_res = client.post('/api/user/settings/', headers={"Authorization": f"Bearer {bearer_token}"},
                                       json={
                                           "key": k2,
                                           "enabled": v2
                                       })
    assert add_median_setting_res.status_code == 201
    assert add_mean_setting_res.status_code == 201

    b1 = json.loads(add_median_setting_res.get_data())
    b2 = json.loads(add_mean_setting_res.get_data())
    assert b1.get("key") == k1
    assert b2.get("key") == k2
    assert b1.get("enabled") == v1
    assert b2.get("enabled") == v2
    # Test to make sure the right users get the right setting:
    k3 = "STANDARD_DEVIATION"
    v3 = True
    client, bearer_token2 = register_and_login_demo_user(client)
    add_stdev_setting_res = client.post('/api/user/settings/',
                                        headers={
                                            "Authorization": f"Bearer {bearer_token2}"},
                                        json={
                                            "key": k3,
                                            "enabled": v3
                                        })
    assert add_stdev_setting_res.status_code == 201
    b3 = json.loads(add_stdev_setting_res.get_data())
    assert b3.get("key") == k3
    assert b3.get("enabled") == v3
    assert b3.get("value") == None

    k4 = "notify"
    v4 = False
    add_email_notif_setting_res = client.post('/api/user/settings/',
                                              headers={
                                                  "Authorization": f"Bearer {bearer_token2}"},
                                              json={
                                                  "key": k4,
                                                  "enabled": v4
                                              })
    assert add_email_notif_setting_res.status_code == 201
    add_email_notif_time_res = client.post('/api/user/settings/',
                                           headers={
                                               "Authorization": f"Bearer {bearer_token2}"},
                                           json={
                                               "key": k4,
                                               "enabled": not v4,
                                               "value": "2000"
                                           })
    assert add_email_notif_time_res.status_code == 201
    b4 = json.loads(add_email_notif_time_res.get_data())
    assert b4.get("key") == k4
    assert b4.get("enabled") == True
    assert b4.get("value") == "2000"

    # def test_get_user_settings(client):
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
                                             "enabled": v1
                                         })
    add_mean_setting_res = client.post('/api/user/settings/', headers={"Authorization": f"Bearer {bearer_token}"},
                                       json={
                                           "key": k2,
                                           "enabled": v2
                                       })
    assert add_median_setting_res.status_code == 201
    assert add_mean_setting_res.status_code == 201
    get_settings_res = client.get(
        "/api/user/settings/", headers={"Authorization": f"Bearer {bearer_token}"})
    assert get_settings_res.status_code == 200
    settings = json.loads(get_settings_res.get_data())

    assert settings[0].get("key") == k1
    assert settings[0].get("enabled") == v1
    assert settings[1].get("key") == k2
    assert settings[1].get("enabled") == v2


def test_change_username(client):
    """
    Tests to change the username of a randomly generated user.
    :param client: The client to perform this action on.
    """
    client, bearer_token = register_and_login_demo_user(client)
    new_username = "Fiddle01"  # Could that name have any meaning associated with it? hmmm
    user_name_change_res = client.put('/api/user/info/', headers={"Authorization": f"Bearer {bearer_token}"}, json={
        "data_type": "username",
        "data": new_username
    })
    assert user_name_change_res.status_code == 200
    assert get_user_by_username(new_username) is not None

    # Create a new account, attempt to change that account to a username that is already taken, should fail
    client, bearer_token2 = register_and_login_demo_user(client)
    user_name_change_res2 = client.put('/api/user/info/', headers={"Authorization": f"Bearer {bearer_token}"}, json={
        "data_type": "username",
        "data": "fiDdLe01"
    })
    assert user_name_change_res2.status_code == 400
    # Then try changing it to a unique username, it should be a success
    new_username2 = "fiDdLe02"
    user_name_change_res3 = client.put('/api/user/info/', headers={"Authorization": f"Bearer {bearer_token}"}, json={
        "data_type": "username",
        "data": new_username2
    })
    assert user_name_change_res3.status_code == 200
    assert get_user_by_username(new_username2) is not None


def test_change_email(client):
    """
    Tests to change the email of a randomly generated user.
    :param client: The client to perform this action on.
    """
    client, bearer_token = register_and_login_demo_user(client)
    new_email = "Fiddle01@gmail.com"  # Could that name have any meaning associated with it? hmmm
    user_name_change_res = client.put('/api/user/info/', headers={"Authorization": f"Bearer {bearer_token}"}, json={
        "data_type": "email",
        "data": new_email
    })
    assert user_name_change_res.status_code == 200
    assert get_user_by_email(new_email) is not None

    # Create a new account, attempt to change that account to an email that is already taken, should fail
    client, bearer_token2 = register_and_login_demo_user(client)
    user_name_change_res2 = client.put('/api/user/info/', headers={"Authorization": f"Bearer {bearer_token}"}, json={
        "data_type": "email",
        "data": "fiDdLe01@gmail.com"
    })
    assert user_name_change_res2.status_code == 400
    # Then try changing it to a unique email, it should be a success
    new_email2 = "Fiddle02@gmail.com"
    user_name_change_res3 = client.put('/api/user/info/', headers={"Authorization": f"Bearer {bearer_token}"}, json={
        "data_type": "email",
        "data": new_email2
    })
    assert user_name_change_res3.status_code == 200
    assert get_user_by_email(new_email2) is not None


def test_change_password(client):
    username = "Hello"
    client, bearer_token = register_and_login_demo_user(client, uname_and_password=username)
    new_password = "Password"
    password_change_res1 = client.put('/api/user/info/',
                                      headers={"Authorization": f"Bearer {bearer_token}"},
                                      json={
                                          "data_type": "password",
                                          "data": username,
                                          "data2": new_password
                                      })
    assert password_change_res1.status_code == 200

    user_credentials = base64.b64encode((f"{username}:{new_password}".encode())).decode('utf-8')
    login_res = client.post('/api/token/', headers={"Authorization": f"Basic {user_credentials}"})
    assert login_res.status_code == 201

    
def test_get_user_by_id(client):
    client, bearer_token = register_and_login_demo_user(client, uname_and_password="test")
    client, bearer_token2 = register_and_login_demo_user(client, uname_and_password="user2")

    make_group_res = client.post('/api/group/',
                                 json={"name": "Epic group of awesome happiness"},
                                 headers={
                                     "Authorization": f"Bearer {bearer_token2}"},
                                 )
    add_member_res = client.put('/api/group/1',
                                json={"invite_users": ["test"]},
                                headers={
                                    "Authorization": f"Bearer {bearer_token2}"},
                                )
    user1_accept_res = client.post('/api/group/accept_invite/1', headers={
        "Authorization": f"Bearer {bearer_token}"})
    assert make_group_res.status_code == 201
    assert add_member_res.status_code == 200
    assert user1_accept_res.status_code == 204

    # Try to get user1's information
    get_user_by_id_res = client.get(
        "/api/user/1", headers={"Authorization": f"Bearer {bearer_token2}"})
    # Check that the request went through
    assert get_user_by_id_res.status_code == 200

    # Ensure that the data was as expected
    body_res = json.loads(get_user_by_id_res.get_data())
    assert body_res.get("id") == 1
    assert body_res.get("username") == "test"


def test_invalid_get_user_by_id(client):
    create_user_res = client.post('/api/user/', json={
        'email': 'test@example.com',
        'username': 'test',
        'password': 'test',
    })
    assert create_user_res.status_code == 201
    client, bearer_token = register_and_login_demo_user(client)

    get_initial_user_res = client.get(
        '/api/user/1', headers={"Authorization": f"Bearer {bearer_token}"})
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

    user_credentials = base64.b64encode(
        (uname_and_password + ":" + uname_and_password).encode()).decode('utf-8')
    assert user_create_response.status_code == 201

    login_response = client.post(
        '/api/token/', headers={"Authorization": f"Basic {user_credentials}"})
    assert login_response.status_code == 201
    bearer_token = json.loads(login_response.get_data()).get("session_token")
    assert bearer_token is not None
    return client, bearer_token

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


def test_user_count(init_client):
    client, tokens = init_client
    init_test_data(client, tokens)

    count_group1 = client.get('/api/user/count/', query_string={
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert count_group1.status_code == 200
    assert count_group1.json.get("groups") == 0

    group_create = client.post('/api/group/', json={'name': 'test'}, headers=auth_header(tokens[0]))
    assert group_create.status_code == 201

    count_group11 = client.get('/api/user/count/', query_string={
    }, headers=auth_header(tokens[0]))
    assert count_group11.status_code == 200
    assert count_group11.json.get("groups") == 1

    count_group2 = client.get('/api/user/count/', query_string={
    }, headers=auth_header(tokens[1]))
    assert count_group2.status_code == 200
    assert count_group2.json.get("groups") == 0

    happiness_token_0 = client.get('api/user/count/', query_string={
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_token_0.status_code == 200
    assert happiness_token_0.json.get("entries") == 7

    happiness_create_response0 = client.post('/api/happiness/', json={
        'value': 2,
        'comment': 'not great day',
        'timestamp': '2024-01-11'
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_create_response0.status_code == 201

    happiness_token_01 = client.get('api/user/count/', query_string={
    }, headers={"Authorization": f"Bearer {tokens[0]}"})
    assert happiness_token_01.status_code == 200
    assert happiness_token_01.json.get("entries") == 8

    happiness_token_1 = client.get('api/user/count/', query_string={
    }, headers={"Authorization": f"Bearer {tokens[1]}"})
    assert happiness_token_1.status_code == 200
    assert happiness_token_1.json.get("entries") == 0

    happiness_create_response1 = client.post('/api/happiness/', json={
        'value': 2.5,
        'comment': 'not great day',
        'timestamp': '2024-01-11'
    }, headers={"Authorization": f"Bearer {tokens[1]}"})
    assert happiness_create_response1.status_code == 201

    happiness_token_11 = client.get('api/user/count/', query_string={
    }, headers={"Authorization": f"Bearer {tokens[1]}"})
    assert happiness_token_11.status_code == 200
    assert happiness_token_11.json.get("entries") == 1



