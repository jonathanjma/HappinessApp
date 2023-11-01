import pytest
from cryptography.fernet import InvalidToken

from api import create_app
from api.app import db
from api.dao.users_dao import *
from api.models.models import Journal
from config import TestConfig


@pytest.fixture
def init_client():
    app = create_app(TestConfig)

    client = app.test_client()
    with app.app_context():
        db.create_all()

        user = User(email='test@example.app', username='user', password='test')
        db.session.add(user)
        db.session.commit()
        token = user.create_token()
        db.session.add(token)
        db.session.commit()

        yield client, token.session_token, user


def auth_key_header(token, key=None):
    return {
        'Authorization': f'Bearer {token}',
        'Password-Key': key
    }


def test_e2e_internals(init_client):
    client, token, user = init_client

    # test encrypt
    password_key = user.derive_password_key('test').decode()
    bad_key = user.derive_password_key('test2').decode()
    encrypted = user.encrypt_data(password_key, 'super secret data').decode()
    with pytest.raises(InvalidToken):
        user.encrypt_data(bad_key, 'super secret data')

    # test decrypt
    assert user.decrypt_data(password_key, encrypted).decode() == 'super secret data'
    with pytest.raises(InvalidToken):
        user.decrypt_data(bad_key, encrypted)

    # test change password
    with pytest.raises(InvalidToken):
        user.change_password('wrong', 'new password')
    user.change_password('test', 'new password')

    # test that new password decrypts data and old one does not
    with pytest.raises(InvalidToken):
        user.decrypt_data(password_key, encrypted)
    password_key = user.derive_password_key('new password').decode()
    assert user.decrypt_data(password_key, encrypted).decode() == 'super secret data'


def test_e2e_recovery_internals(init_client):
    client, token, user = init_client
    password_key = user.derive_password_key('test').decode()
    encrypted = user.encrypt_data(password_key, 'super secret data').decode()

    # test add recovery phrase
    user.add_key_recovery('test', 'rescue')
    with pytest.raises(InvalidToken):
        user.reset_password('wrong', 'bad rescue')

    # test reset password with recovery phrase
    with pytest.raises(InvalidToken):
        user.reset_password('test3', 'bad rescue')
    user.reset_password('test3', 'rescue')

    # test that new password decrypts data and old one does not
    with pytest.raises(InvalidToken):
        user.decrypt_data(password_key, encrypted)
    password_key = user.derive_password_key('test3').decode()
    assert user.decrypt_data(password_key, encrypted).decode() == 'super secret data'

def test_jwt(init_client):
    client, token, user = init_client

    bad_get = client.get('/api/journal/key', json={'password': 'wrong'},
                         headers=auth_key_header(token))
    assert bad_get.status_code == 401

    get_no_token = client.get('/api/journal/', headers=auth_key_header(token))
    assert get_no_token.status_code == 400

    get_invalid_token = client.get('/api/journal/', headers=auth_key_header(token, 'not real'))
    assert get_invalid_token.status_code == 400

    expired_token = user.generate_password_key_token('test', 0)
    get_exp_token = client.get('/api/journal/', headers=auth_key_header(token, expired_token))
    assert get_exp_token.status_code == 400

    get_key = client.get('/api/journal/key', json={'password': 'test'},
                         headers=auth_key_header(token))
    assert get_key.status_code == 200

    get_valid = client.get('/api/journal/',
                           headers=auth_key_header(token, get_key.headers['Password-Key']))
    assert get_valid.status_code == 200


def test_create_get(init_client):
    client, token, user = init_client
    key_token = user.generate_password_key_token('test')

    create1 = client.post('/api/journal/', json={'data': 'secret', 'timestamp': '2023-10-20'},
                          headers=auth_key_header(token, key_token))
    create2 = client.post('/api/journal/', json={'data': 'secret2', 'timestamp': '2023-10-21'},
                          headers=auth_key_header(token, key_token))
    create_dup = client.post('/api/journal/', json={'data': 'secret3', 'timestamp': '2023-10-21'},
                             headers=auth_key_header(token, key_token))
    assert create1.status_code == 201 and create2.status_code == 201
    assert create_dup.status_code == 400
    assert Journal.query.first().data.decode() != 'secret'

    get1 = client.get('/api/journal/', query_string={'count': 1, 'page': 2},
                      headers=auth_key_header(token, key_token))
    get2 = client.get('/api/journal/', query_string={'count': 1, 'page': 1},
                      headers=auth_key_header(token, key_token))
    assert get1.status_code == 200 and get2.status_code == 200
    assert get1.json[0]['data'] == 'secret' and get2.json[0]['data'] == 'secret2'

def create_test_entries(client, token, key_token):
    client.post('/api/journal/', json={'data': 'secret', 'timestamp': '2023-10-20'},
                headers=auth_key_header(token, key_token))
    client.post('/api/journal/', json={'data': 'secret2', 'timestamp': '2023-10-21'},
                headers=auth_key_header(token, key_token))

def test_change_password_get(init_client):
    client, token, user = init_client
    key_token = user.generate_password_key_token('test')
    create_test_entries(client, token, key_token)

    change_password_bad = client.put('/api/user/info/',
                                     json={'data_type': 'password', 'data': 'wrong', 'data2': 'test2'},
                                     headers=auth_key_header(token))
    assert change_password_bad.status_code == 401

    change_password = client.put('/api/user/info/',
                                 json={'data_type': 'password', 'data': 'test', 'data2': 'test2'},
                                 headers=auth_key_header(token))
    assert change_password.status_code == 200

    bad_old_key = client.get('/api/journal/', headers=auth_key_header(token, key_token))
    assert bad_old_key.status_code == 400

    key_token = user.generate_password_key_token('test2')
    get = client.get('/api/journal/', headers=auth_key_header(token, key_token))
    assert get.status_code == 200
    assert get.json[1]['data'] == 'secret' and get.json[0]['data'] == 'secret2'


def test_reset_password_recovery_get(init_client):
    client, token, user = init_client
    key_token = user.generate_password_key_token('test')
    create_test_entries(client, token, key_token)

    add_recovery_bad = client.put('/api/user/info/',
                                  json={'data_type': 'key_recovery_phrase', 'data': 'wrong', 'data2': 'help'},
                                  headers=auth_key_header(token))
    assert add_recovery_bad.status_code == 401

    add_recovery = client.put('/api/user/info/',
                              json={'data_type': 'key_recovery_phrase', 'data': 'test', 'data2': 'help'},
                              headers=auth_key_header(token))
    assert add_recovery.status_code == 200

    reset_token = user.generate_password_reset_token()
    bad_reset_recovery = client.post('/api/user/reset_password/' + reset_token,
                                     json={'password': 'W password', 'recovery_phrase': 'nope'})
    assert bad_reset_recovery.status_code == 400

    reset_password = client.post('/api/user/reset_password/' + reset_token,
                                 json={'password': 'W password', 'recovery_phrase': 'HELP'})
    assert reset_password.status_code == 204

    bad_old_key = client.get('/api/journal/', headers=auth_key_header(token, key_token))
    assert bad_old_key.status_code == 400

    key_token = user.generate_password_key_token('W password')
    get = client.get('/api/journal/', headers=auth_key_header(token, key_token))
    assert get.status_code == 200
    assert get.json[1]['data'] == 'secret' and get.json[0]['data'] == 'secret2'


def test_edit(init_client):
    client, token, user = init_client
    key_token = user.generate_password_key_token('test')
    create_test_entries(client, token, key_token)

    bad_edit = client.put('/api/journal/?id=2', headers=auth_key_header(token))
    assert bad_edit.status_code == 400

    bad_id_edit = client.put('/api/journal/?id=3', json={'data': 'happiness app'},
                             headers=auth_key_header(token, key_token))
    assert bad_id_edit.status_code == 404

    bad_date_edit = client.put('/api/journal/?date=2023-10-01', json={'data': 'happiness app'},
                             headers=auth_key_header(token, key_token))
    assert bad_date_edit.status_code == 404

    edit1 = client.put('/api/journal/?id=1', json={'data': 'happiness app'},
                      headers=auth_key_header(token, key_token))
    edit2 = client.put('/api/journal/?date=2023-10-21', json={'data': 'happiness app2'},
                       headers=auth_key_header(token, key_token))
    assert edit1.status_code == 200 and edit2.status_code == 200

    get = client.get('/api/journal/', headers=auth_key_header(token, key_token))
    assert get.json[0]['data'] == 'happiness app2' and get.json[1]['data'] == 'happiness app'


def test_delete(init_client):
    client, token, user = init_client
    key_token = user.generate_password_key_token('test')
    create_test_entries(client, token, key_token)
    client.post('/api/journal/', json={'data': 'secret3', 'timestamp': '2023-10-22'},
                headers=auth_key_header(token, key_token))

    delete1 = client.delete('/api/journal/?id=1', headers=auth_key_header(token, key_token))
    delete2 = client.delete('/api/journal/?date=2023-10-21', headers=auth_key_header(token, key_token))
    assert delete1.status_code == 204 and delete2.status_code == 204

    get = client.get('/api/journal/', headers=auth_key_header(token, key_token))
    assert len(get.json) == 1
    assert get.json[0]['data'] == 'secret3'
