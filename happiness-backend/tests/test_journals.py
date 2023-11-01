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


def auth_key_header(token, key):
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


def test_create_get(init_client):
    client, token, user = init_client
    password_key = user.derive_password_key('test').decode()

    bad_create = client.post('/api/journal/', json={'data': 'secret'},
                             headers=auth_key_header(token, None))
    assert bad_create.status_code == 400

    bad_key = client.post('/api/journal/', json={'data': 'secret'},
                          headers=auth_key_header(token, user.derive_password_key('test2')))
    assert bad_key.status_code == 400

    create1 = client.post('/api/journal/', json={'data': 'secret'},
                          headers=auth_key_header(token, password_key))
    create2 = client.post('/api/journal/', json={'data': 'secret2'},
                          headers=auth_key_header(token, password_key))
    assert create1.status_code == 201 and create2.status_code == 201
    assert Journal.query.first().data.decode() != 'secret'

    get1 = client.get('/api/journal/', query_string={'count': 1, 'page': 2},
                      headers=auth_key_header(token, password_key))
    get2 = client.get('/api/journal/', query_string={'count': 1, 'page': 1},
                      headers=auth_key_header(token, password_key))
    assert get1.status_code == 200 and get2.status_code == 200
    assert get1.json[0]['data'] == 'secret' and get2.json[0]['data'] == 'secret2'


def test_change_password_get(init_client):
    client, token, user = init_client
    password_key = user.derive_password_key('test').decode()
    client.post('/api/journal/', json={'data': 'secret'}, headers=auth_key_header(token, password_key))
    client.post('/api/journal/', json={'data': 'secret2'}, headers=auth_key_header(token, password_key))

    change_password = client.put('/api/user/info/',
                            json={'data_type': 'password', 'data': 'test2'},
                            headers=auth_key_header(token, password_key))
    assert change_password.status_code == 200

    bad_get = client.get('/api/journal/', headers=auth_key_header(token, password_key))
    assert bad_get.status_code == 400

    get = client.get('/api/journal/', headers=auth_key_header(token, user.derive_password_key('test2')))
    assert get.status_code == 200
    assert get.json[1]['data'] == 'secret' and get.json[0]['data'] == 'secret2'


def test_reset_password_recovery_get(init_client):
    client, token, user = init_client
    password_key = user.derive_password_key('test').decode()
    client.post('/api/journal/', json={'data': 'secret'}, headers=auth_key_header(token, password_key))
    client.post('/api/journal/', json={'data': 'secret2'}, headers=auth_key_header(token, password_key))

    add_recovery = client.put('/api/user/info/',
                              json={'data_type': 'key_recovery_phrase', 'data': 'help'},
                              headers=auth_key_header(token, password_key))
    assert add_recovery.status_code == 200

    reset_token = generate_confirmation_token('test@example.app')

    bad_reset = client.post('/api/user/reset_password/' + reset_token,
                            json={'password': 'W password', 'recovery_phrase': 'nope'})
    assert bad_reset.status_code == 400

    reset_password = client.post('/api/user/reset_password/' + reset_token,
                                 json={'password': 'W password', 'recovery_phrase': 'HELP'})
    assert reset_password.status_code == 204

    bad_get = client.get('/api/journal/', headers=auth_key_header(token, password_key))
    assert bad_get.status_code == 400

    get = client.get('/api/journal/', headers=auth_key_header(token, user.derive_password_key('W password')))
    assert get.status_code == 200
    assert get.json[1]['data'] == 'secret' and get.json[0]['data'] == 'secret2'


def test_edit(init_client):
    client, token, user = init_client
    password_key = user.derive_password_key('test').decode()
    client.post('/api/journal/', json={'data': 'secret'}, headers=auth_key_header(token, password_key))
    client.post('/api/journal/', json={'data': 'secret2'}, headers=auth_key_header(token, password_key))

    bad_edit = client.put('/api/journal/?id=2', headers=auth_key_header(token, None))
    assert bad_edit.status_code == 400

    edit = client.put('/api/journal/?id=2', json={'data': 'happiness app'},
                      headers=auth_key_header(token, password_key))
    assert edit.status_code == 200

    get1 = client.get('/api/journal/', headers=auth_key_header(token, password_key))
    assert get1.json[0]['data'] == 'happiness app'


def test_delete(init_client):
    client, token, user = init_client
    password_key = user.derive_password_key('test').decode()
    client.post('/api/journal/', json={'data': 'secret'}, headers=auth_key_header(token, password_key))
    client.post('/api/journal/', json={'data': 'secret2'}, headers=auth_key_header(token, password_key))

    delete = client.delete('/api/journal/?id=2', headers=auth_key_header(token, password_key))
    assert delete.status_code == 204

    get = client.get('/api/journal/', headers=auth_key_header(token, password_key))
    assert len(get.json) == 1
    assert get.json[0]['data'] == 'secret'
