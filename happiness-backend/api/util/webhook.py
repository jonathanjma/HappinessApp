import requests
from flask import current_app

from api.dao.groups_dao import get_group_by_id
from api.models.models import Happiness, User

# temporary table for recently created entries
db_discord_map = {}

def process_webhooks(user: User, happiness: Happiness, on_edit=False):
    if current_app.config["TESTING"]: return

    if get_group_by_id(51) in user.groups: # suite group
        send_webhook(user, happiness, current_app.config["AST_WEBHOOK_URL"], on_edit)

def send_webhook(user: User, happiness: Happiness, url: str, on_edit: bool):
    payload = {
        "content": None,
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
        ]
    }
    # for new entries: add bot info, send entry, store discord msg id
    if not on_edit:
        payload = {
            **payload,
            "username": "Happiness Bot",
            "avatar_url": "https://github.com/jonathanjma/HappinessApp/blob/main/imgs/icon.png?raw=true",
        }
        res = requests.post(url + '?wait=True', json=payload)
        db_discord_map[happiness.id] = res.json()["id"]
    # for (recent) entry edits: look up discord msg id and send updated entry
    elif happiness.id in db_discord_map.keys():
        requests.patch(f'{url}/messages/{db_discord_map[happiness.id]}', json=payload)
