import csv
import os
from datetime import datetime, timedelta

import redis
from dateutil import parser
from dotenv import load_dotenv
from flask import render_template
from rq import Queue

from api import create_app
from api.dao import happiness_dao, users_dao
from api.email_methods import send_email_helper
from api.models import Token, Setting

"""
jobs.py contains all scheduled jobs that will be queued by scheduler.py
"""

app = create_app()
app.app_context().push()

load_dotenv()
redis_url = os.getenv('REDISCLOUD_URL')

conn = redis.from_url(redis_url)
q = Queue('happiness-backend-jobs', connection=conn)


def clear_exported_happiness():
    """
    Deletes all files in the `export` folder that are older than 1 hour.
    """
    minutes5ago = (datetime.now() - timedelta(hours=1))
    folder_path = "export"

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            created_time = datetime.fromtimestamp(os.path.getctime(file_path))

            if created_time < minutes5ago:
                os.remove(file_path)


def clean_tokens():
    """
    Deletes all expired tokens
    """
    Token.clean()


def export_happiness(user_id):
    """
    Export Happiness
    Exports a user's happiness, returning a CSV file containing the values, comments, and timestamps.
    """
    current_user = users_dao.get_user_by_id(user_id)
    entries = happiness_dao.get_user_happiness(current_user.id)

    def to_dict_entry(n):
        new_dict = n.__dict__
        new_dict.pop('_sa_instance_state')
        new_dict.pop('user_id')
        new_dict.pop('id')

        return new_dict

    entries_dict = map(to_dict_entry, entries)
    fields = ['value', 'comment', 'timestamp']
    file_path = "export/{filename}"
    with open(file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(entries_dict)
    with open(file_path, 'r', newline='') as file:
        send_email_helper(
            subject="Your Happiness Export :)",
            sender="noreply@happinessapp.org",
            recipients=[current_user.email],
            text_body=render_template('happiness_export.txt', user=current_user),
            html_body=render_template('happiness_export.html', user=current_user),
            attachments=[(f"{current_user.username} happiness export.csv", "text/csv", file.read())]
        )
    # Leftover files are deleted by a scheduled job, so no need to be worried about that here.


def send_notification_email(user_id):
    """
    Sends a happiness app reminder notification email to the given email.
    Requires: user is missing at least 1 entry in the past week
    """
    user_to_send = users_dao.get_user_by_id(user_id)
    dates_should_be_present = [
        (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 7)
    ]
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    last_week = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
    entries = happiness_dao.get_happiness_by_timestamp(start=last_week, end=yesterday, user_id=user_id)
    entries = list(filter(lambda x: x is not None, entries))
    entries = [x.timestamp.strftime("%Y-%m-%d") for x in entries]

    for timestamp in entries:
        if timestamp in dates_should_be_present:
            dates_should_be_present.remove(timestamp)

    missing_dates_str = ""
    for i, d in enumerate(dates_should_be_present):
        missing_dates_str += d[5:]
        if i != len(dates_should_be_present) - 1:
            missing_dates_str += ", "

    send_email_helper(
        subject="Enter Your Happiness :)",
        sender="noreply@happinessapp.org",
        recipients=[user_to_send.email],
        text_body=render_template('notify_happiness.txt', user=user_to_send, dates=missing_dates_str),
        html_body=render_template('notify_happiness.html', user=user_to_send, dates=missing_dates_str)
    )


def queue_send_notification_emails():
    """
    Adds all notification email requests to the redis queue
    A user will be a part of a notification email request if they satisfy the following conditions:
    Has a setting with the key "notify"
    The value of the setting is a 24-hour time with hours and minutes and matches the current time
    They have less than 6 Happiness entries from yesterday to 1 week before today
    TODO test new implementation!
    """
    # All happiness app entries are in UTC, so it is fine that the current time is in UTC.
    current_time = str(datetime.now().time().strftime("%H:%M"))
    """
    Suppose it is 11:30PM EST, a user has a notify setting for 3:30AM UTC
    This job runs, and the user is checked for if they are missing happiness app entries 1 day in the past.
    
    """
    to_notify = Setting.query.filter(Setting.key == "notify",
                                     Setting.enabled.is_(True)).all()

    # Helper function for later
    def get_current_time_from_timezone_by_iso_time(time: str):
        """
        Gets a date object containing the current time in the timezone of the time given in the parameter
        :param time: A timezone string compliant with ISO 8601
        :return: a date time object containing the current time in said timezone
        """
        # Parse the input string to a datetime object
        time_in_given_tz = parser.isoparse(time)

        # Get timezone of the parsed datetime
        timezone = time_in_given_tz.tzinfo
        print(f"timezone = {timezone}")

        # Get current time in timezone of the parsed datetime
        now_in_given_tz = datetime.now(tz=timezone)

        return now_in_given_tz

    def get_utc_time(time):
        """
        Gets the time of an ISO 8601 compliant string in UTC time, in the %H%M format.
        """
        # TODO
        return ""

    for setting in to_notify:
        notify_time = setting.value
        # Check if user is missing happiness entries:
        if get_utc_time(notify_time) == current_time:
            yesterday = (get_current_time_from_timezone_by_iso_time(notify_time) - timedelta(days=1)).replace(hour=23,
                                                                                                              minute=59,
                                                                                                              second=59)
            last_week = (get_current_time_from_timezone_by_iso_time(notify_time) - timedelta(days=6)).replace(hour=0,
                                                                                                              minute=0,
                                                                                                              second=0)
            yesterday_utc = get_utc_time(yesterday)
            last_week_utc = get_utc_time(last_week)
            entries = happiness_dao.get_happiness_by_timestamp(start=last_week_utc, end=yesterday_utc,
                                                               user_id=setting.user_id)
            entries = list(filter(lambda x: x is not None, entries))
            if len(entries) < 6:
                # They are missing an entry, and we are guaranteed to send an email which is expensive
                # Therefore we queue another job to redis
                q.enqueue("jobs.jobs.send_notification_email", setting.user_id)
