import json
import os

import requests
from filelock import FileLock
from flask import current_app

from api.dao.groups_dao import get_group_by_id
from api.models.models import Happiness, User

# temporary table for recently created entries
# (use dict for vales since 1 happiness entry can be sent to multiple webhooks)
# (store in file since we have multiple web workers...)
DISCORD_MAP_FILE = "discord_map.json"
LOCK_FILE = "discord_map.json.lock"

def read_discord_map():
    if not os.path.exists(DISCORD_MAP_FILE): return {}
    with FileLock(LOCK_FILE):
        with open(DISCORD_MAP_FILE, 'r') as f:
            return json.load(f)

def write_discord_map(discord_map):
    with FileLock(LOCK_FILE):
        with open(DISCORD_MAP_FILE, 'w') as f:
            json.dump(discord_map, f)

def process_webhooks(user: User, happiness: Happiness, on_edit=False):
    if current_app.config["TESTING"]: return

    if get_group_by_id(51) in user.groups: # suite group
        send_webhook(user, happiness, current_app.config["AST_WEBHOOK_URL"], on_edit)
    if get_group_by_id(9) in user.groups: # HS friends group
        send_webhook(user, happiness, current_app.config["BOIS_WEBHOOK_URL"], on_edit)

def send_webhook(user: User, happiness: Happiness, url: str, on_edit: bool):
    # 2048 char limit for description
    description = (f"**Score** \n{str(happiness.value)}" +
                   (f"\n\n**Comment**\n{happiness.comment[:2048]}" if happiness.comment else ""))
    payload = {
        "embeds": [
            {
                "title": happiness.timestamp.strftime('%m/%d') + " Happiness Entry",
                "description": description,
                "color": int("ecc665", 16),
                "author": {
                    "name": "@" + user.username,
                    "url": "https://www.happinessapp.me/profile/" + str(user.id),
                    "icon_url": user.profile_picture
                }
            }
        ]
    }
    # for new entries: add bot info, send entry, store discord msg id
    discord_map = read_discord_map()
    h_id = str(happiness.id)
    if not on_edit:
        payload = {
            **payload,
            "username": "Happiness Bot",
            "avatar_url": "https://github.com/jonathanjma/HappinessApp/blob/main/imgs/icon.png?raw=true",
        }
        res = requests.post(url + '?wait=True', json=payload)
        if h_id not in discord_map: discord_map[h_id] = {}
        discord_map[h_id][url] = res.json()["id"]
        write_discord_map(discord_map)
    # for (recent) entry edits: look up discord msg id and send updated entry
    elif h_id in discord_map.keys():
        res = requests.patch(f'{url}/messages/{discord_map[h_id][url]}', json=payload)

"""
for wrapped:
{
  "content": "@everyone",
  "embeds": [
    {
      "title": "Happiness App Wrapped 2024 Now Available!",
      "description": "Hi everyone, \n\nJust wanted to make an announcement that the 2024 Happiness App Wrapped is now available! So if you used the app this year and wanted some fun insights into your scores, click the link above or visit https://www.happinessapp.me/wrapped. And while you are there, don't forget to click the share button to share your stats with your friends! \n\nThanks for using Happiness App this year!",
      "url": "https://www.happinessapp.me/wrapped",
      "color": 15517285,
      "author": {
        "name": "Happiness App",
        "url": "https://www.happinessapp.me",
        "icon_url": "https://raw.githubusercontent.com/jonathanjma/HappinessApp/refs/heads/main/imgs/icon.png"
      }
    }
  ],
  "username": "Happiness Bot",
  "avatar_url": "https://github.com/jonathanjma/HappinessApp/blob/main/imgs/icon.png?raw=true"
}
"""