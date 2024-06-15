import requests
from flask import current_app

from api.dao.groups_dao import get_group_by_id
from api.models.models import Happiness, User

def process_webhooks(user: User, happiness: Happiness):
    if get_group_by_id(51) in user.groups: # suite group
        send_webhook(user, happiness, current_app.config["AST_WEBHOOK_URL"])

def send_webhook(user: User, happiness: Happiness, url: str):
    payload = {
        "content": "",
        "embeds": [
            {
                "title": happiness.timestamp.strftime('%m/%d') + " Happiness Entry",
                "color": int("ecc665", 16),
                "fields": [
                    {
                        "name": "Score",
                        "value": str(happiness.value)
                    },
                    {
                        "name": "Comment",
                        "value": happiness.comment
                    }
                ],
                "author": {
                    "name": "@" + user.username,
                    "url": "https://www.happinessapp.me/profile/" + str(user.id),
                    "icon_url": user.profile_picture
                }
            }
        ],
        "username": "Happiness Bot",
        "avatar_url": "https://github.com/jonathanjma/HappinessApp/blob/main/imgs/icon.png?raw=true",
    }
    requests.post(url, json=payload)