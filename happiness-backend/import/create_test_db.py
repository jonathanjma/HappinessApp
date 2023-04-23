import pickle

import requests

create_users_groups = True
port = "5000"

if create_users_groups:
    new_user1 = requests.post(f'http://localhost:{port}/api/user/',
                              json={
                                  "email": "ayw29@cornell.edu",
                                  "username": "alex",
                                  "password": "alex"
                              })
    new_user2 = requests.post(f'http://localhost:{port}/api/user/',
                              json={
                                  "email": "jjm498@cornell.edu",
                                  "username": "jonathan",
                                  "password": "jonathan"
                              })
    new_user3 = requests.post(f'http://localhost:{port}/api/user/',
                              json={
                                  "email": "zes4@cornell.edu",
                                  "username": "zach",
                                  "password": "zach"
                              })
    assert new_user1.status_code == new_user2.status_code == new_user3.status_code == 201
    print('users created')

    get_token = requests.post(f'http://localhost:{port}/api/token/', auth=("alex", "alex"))
    assert get_token.status_code == 201
    token = get_token.json()['session_token']

    new_group = requests.post(f'http://localhost:{port}/api/group/',
                              headers={"Authorization": f"Bearer {token}"},
                              json={
                                  "name": "hello world 🌍"
                              })
    add_members = requests.put(f'http://localhost:{port}/api/group/1',
                               headers={"Authorization": f"Bearer {token}"},
                               json={
                                   "add_users": [
                                       {"username": "jonathan"},
                                       {"username": "zach"}
                                   ]
                               })
    assert new_group.status_code == 201 and add_members.status_code == 200
    print('group created')

with open('happiness_import.pick', 'rb') as f:
    all_user_data = pickle.load(f)

import_data = requests.post(f'http://localhost:{port}/api/happiness/import',
                            headers={"Content-Type": "application/json"},
                            data=all_user_data)
print(import_data.text)
