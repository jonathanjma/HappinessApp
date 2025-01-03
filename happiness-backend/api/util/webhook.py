import requests
from flask import current_app
from collections import defaultdict

from api.dao.groups_dao import get_group_by_id
from api.models.models import Happiness, User

# temporary table for recently created entries
# (use dict for vales since 1 happiness entry can be sent to multiple webhooks)
db_discord_map = defaultdict(dict)

def process_webhooks(user: User, happiness: Happiness, on_edit=False):
    if current_app.config["TESTING"]: return

    if get_group_by_id(51) in user.groups: # suite group
        send_webhook(user, happiness, current_app.config["AST_WEBHOOK_URL"], on_edit)
    if get_group_by_id(9) in user.groups: # HS friends group
        send_webhook(user, happiness, current_app.config["BOIS_WEBHOOK_URL"], on_edit)

def send_webhook(user: User, happiness: Happiness, url: str, on_edit: bool):
    # 2048 char limit for description
    description = (f"**Score** \n{str(happiness.value)}" +
                   f"\n\n**Comment**\n{happiness.comment[:2048]}") if happiness.comment else ""
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
    if not on_edit:
        payload = {
            **payload,
            "username": "Happiness Bot",
            "avatar_url": "https://github.com/jonathanjma/HappinessApp/blob/main/imgs/icon.png?raw=true",
        }
        res = requests.post(url + '?wait=True', json=payload)
        print(f"webhook post sent: {res.status_code}, {res.reason}")
        db_discord_map[happiness.id][url] = res.json()["id"]
    # for (recent) entry edits: look up discord msg id and send updated entry
    elif happiness.id in db_discord_map.keys():
        res = requests.patch(f'{url}/messages/{db_discord_map[happiness.id][url]}', json=payload)
        print(f"webhook edit sent: {res.status_code}, {res.reason}")

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