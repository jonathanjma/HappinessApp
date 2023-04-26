import pickle
import json

import datetime
import requests

# date of earliest happiness entry
since = datetime.datetime(2022, 8, 15)
backend_url = "https://happiness-app-backend.herokuapp.com"
#backend_url = "http://localhost:5000"

# false: only import happiness
# true: create test users/group and import happiness
create_users_groups = False

if create_users_groups:
    new_user1 = requests.post(f'{backend_url}/api/user/',
                              json={
                                  "email": "ayw29@cornell.edu",
                                  "username": "alex",
                                  "password": "alex"
                              })
    new_user2 = requests.post(f'{backend_url}/api/user/',
                              json={
                                  "email": "jjm498@cornell.edu",
                                  "username": "jonathan",
                                  "password": "jonathan"
                              })
    new_user3 = requests.post(f'{backend_url}/api/user/',
                              json={
                                  "email": "zes4@cornell.edu",
                                  "username": "zach",
                                  "password": "zach"
                              })
    # requests.post(f'{backend_url}/api/user/',
    #               json={
    #                   "email": "aaron@cornell.edu",
    #                   "username": "aaron",
    #                   "password": "aaron"
    #               })
    # requests.post(f'{backend_url}/api/user/',
    #               json={
    #                   "email": "sasha@cornell.edu",
    #                   "username": "sasha",
    #                   "password": "sasha"
    #               })
    # requests.post(f'{backend_url}/api/user/',
    #               json={
    #                   "email": "andrew@cornell.edu",
    #                   "username": "andrew",
    #                   "password": "andrew"
    #               })
    # requests.post(f'{backend_url}/api/user/',
    #               json={
    #                   "email": "shashank@cornell.edu",
    #                   "username": "shashank",
    #                   "password": "shashank"
    #               })

    assert new_user1.status_code == new_user2.status_code == new_user3.status_code == 201
    print('users created')

    get_token = requests.post(f'{backend_url}/api/token/', auth=("alex", "alex"))
    assert get_token.status_code == 201
    token = get_token.json()['session_token']

    new_group = requests.post(f'{backend_url}/api/group/',
                              headers={"Authorization": f"Bearer {token}"},
                              json={
                                  "name": "hello world 🌍"
                              })
    add_members = requests.put(f'{backend_url}/api/group/1',
                               headers={"Authorization": f"Bearer {token}"},
                               json={
                                   "add_users": ["jonathan", "zach"]
                               })
    assert new_group.status_code == 201 and add_members.status_code == 200
    print('group created')

with open('happiness_import.pick', 'rb') as f:
    all_user_data = pickle.load(f)

all_user_data = list(
    filter(lambda x: datetime.datetime.strptime(x['timestamp'], "%Y-%m-%d") >= since,
           all_user_data))

import_data = requests.post(f'{backend_url}/api/happiness/import',
                            headers={"Content-Type": "application/json"},
                            data=json.dumps(all_user_data))
print(import_data.text)
