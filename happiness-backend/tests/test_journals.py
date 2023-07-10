import pytest
from cryptography.fernet import InvalidToken

from api import create_app
from api.app import db
from api.models import Journal
from api.dao.users_dao import *
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


def test_e2e(init_client):
    client, token, user = init_client

    pwd_key = user.derive_pwd_key('test').decode()
    bad_key = user.derive_pwd_key('test2').decode()
    encrypted = user.encrypt_data(pwd_key, 'super secret data').decode()
    with pytest.raises(InvalidToken):
        user.encrypt_data(bad_key, 'super secret data')

    assert user.decrypt_data(pwd_key, encrypted).decode() == 'super secret data'
    with pytest.raises(InvalidToken):
        user.decrypt_data(bad_key, encrypted)

    with pytest.raises(InvalidToken):
        user.change_password('password', bad_key)
    user.change_password('password', pwd_key)

    with pytest.raises(InvalidToken):
        user.decrypt_data(pwd_key, encrypted)
    new_pwd_key = user.derive_pwd_key('password').decode()
    assert user.decrypt_data(new_pwd_key, encrypted).decode() == 'super secret data'


def test_journals(init_client):
    client, token, user = init_client
    pwd_key = user.derive_pwd_key('test').decode()

    bad_create = client.post('/api/journal/', json={'data': 'secret'},
                             headers=auth_key_header(token, None))
    assert bad_create.status_code == 400

    bad_key = client.post('/api/journal/', json={'data': 'secret'},
                          headers=auth_key_header(token, user.derive_pwd_key('test2')))
    assert bad_key.status_code == 400

    create1 = client.post('/api/journal/', json={'data': 'secret'},
                          headers=auth_key_header(token, pwd_key))
    create2 = client.post('/api/journal/', json={'data': 'secret2'},
                          headers=auth_key_header(token, pwd_key))
    assert create1.status_code == 201 and create2.status_code == 201
    assert Journal.query.first().data.decode() != 'secret'

    get1 = client.get('/api/journal/', query_string={'count': 1, 'page': 2},
                      headers=auth_key_header(token, pwd_key))
    get2 = client.get('/api/journal/', query_string={'count': 1, 'page': 1},
                      headers=auth_key_header(token, pwd_key))
    assert get1.status_code == 200 and get2.status_code == 200
    assert get1.json[0]['data'] == 'secret' and get2.json[0]['data'] == 'secret2'

    change_pwd = client.put('/api/user/info/',
                            json={'data_type': 'password', 'data': 'test2'},
                            headers=auth_key_header(token, pwd_key))
    assert change_pwd.status_code == 200

    bad_get = client.get('/api/journal/', headers=auth_key_header(token, pwd_key))
    assert bad_get.status_code == 400

    get = client.get('/api/journal/', headers=auth_key_header(token, user.derive_pwd_key('test2')))
    assert get.status_code == 200
    assert get.json[1]['data'] == 'secret' and get.json[0]['data'] == 'secret2'