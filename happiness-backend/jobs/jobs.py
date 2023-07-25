import csv
import os
import uuid
from datetime import datetime, timedelta

import redis
from dotenv import load_dotenv
from flask import render_template, db
from rq import Queue

from api import create_app
from api.dao import happiness_dao, users_dao
from api.email_methods import send_email_helper
from api.models import Token, Setting, Community, Statistic

import statistics

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
            text_body=render_template(
                'happiness_export.txt', user=current_user),
            html_body=render_template(
                'happiness_export.html', user=current_user),
            attachments=[
                (f"{current_user.username} happiness export.csv", "text/csv", file.read())]
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
    entries = happiness_dao.get_happiness_by_timestamp(
        start=last_week, end=yesterday, user_id=user_id)
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
        text_body=render_template(
            'notify_happiness.txt', user=user_to_send, dates=missing_dates_str),
        html_body=render_template(
            'notify_happiness.html', user=user_to_send, dates=missing_dates_str)
    )


def queue_send_notification_emails():
    """
    Adds all notification email requests to the redis queue
    A user will be a part of a notification email request if they satisfy the following conditions:
    Has a setting with the key "notify"
    The value of the setting is a 24-hour time with hours and minutes and matches the current time
    They have less than 6 Happiness entries from yesterday to 1 week before today
    """
    current_time = str(datetime.now().time().strftime("%H:%M"))
    # For some reason, the between query for SQLAlchemy seems to be exclusive for the end date
    # This is very confusing since according to the docs between should be inclusive
    # It translates to BETWEEN in SQL:
    # https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.between
    # BETWEEN is inclusive: https://www.w3schools.com/sql/sql_between.asp
    # But it works so for now I will keep it.

    today = (datetime.now())
    last_week = (datetime.now() - timedelta(days=6))
    to_notify = Setting.query.filter(Setting.value == str(current_time), Setting.key == "notify",
                                     Setting.enabled.is_(True)).all()
    print(f"to_notify: {to_notify}")
    for setting in to_notify:
        # Check if user is missing happiness entries:
        # print(f"start: {last_week}")
        # print(f"end: {today}")
        entries = happiness_dao.get_happiness_by_timestamp(
            start=last_week, end=today, user_id=setting.user_id)
        entries = list(filter(lambda x: x is not None, entries))
        # print(f"entries: {entries}")
        # print("timestamps: \n\n")
        if len(entries) < 6:
            # They are missing an entry, and we are guaranteed to send an email which is expensive
            # Therefore we queue another job to redis
            q.enqueue("jobs.jobs.send_notification_email", setting.user_id)


def calculate_global_statistic(community_id):
    """
    Calculates global statistics for all communities, and then adds each entry to the backend.
    """
    to_calculate = Community.query.all()
    print(f"to calculate: {to_calculate}")

    for community in to_calculate:
        date = (datetime.now() - timedelta(days=1))
        user_ids = community.users
        happiness_entries = happiness_dao.get_happiness_by_group_timestamp(
            user_ids, date, date)

        if len(happiness_entries) > 0:
            happiness_values = list(
                map(lambda x: x['value'], happiness_entries))

            mean = statistics.mean(happiness_values)
            median = statistics.median(happiness_values)
            stdev = statistics.stdev(happiness_values)
            minval = min(happiness_values)
            maxval = max(happiness_values)

            quartiles = statistics.quantiles()
            firstquar = quartiles[0]
            thirdquar = quartiles[2]

            statistic = Statistic(community_id=community_id, mean=mean, median=median,
                                  stdev=stdev, minval=minval, maxval=maxval, firstquar=firstquar,
                                  thirdquar=thirdquar, timestamp=date)
            db.session.add(statistic)
            db.session.commit()
