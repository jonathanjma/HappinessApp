import csv
import os
import uuid
from datetime import datetime, timedelta

from flask import render_template

from api import create_app
from api.dao import happiness_dao, users_dao
from api.email_methods import send_email_helper
from api.models import Token, Setting

"""
jobs.py contains all scheduled jobs that will be queued by scheduler.py
"""

app = create_app()
app.app_context().push()


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
    filename = f"happiness_{uuid.uuid4()}.csv"
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


def send_notification_emails(user_id):
    """
    Sends a happiness app reminder notification email to the given email.
    """
    user_to_send = users_dao.get_user_by_id(user_id)
    dates_should_be_present = [
        (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 7)
    ]
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    last_week = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
    entries = happiness_dao.get_happiness_by_timestamp(start=last_week, end=yesterday, user_id=user_id)
    for e in entries:
        if e.timestamp in dates_should_be_present:
            dates_should_be_present.remove(e.timestamp)
    missing_dates_str = "\n".join(dates_should_be_present)

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
    """
    current_time = datetime.now().time()
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    last_week = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")

    to_notify = Setting.query.filter(Setting.value == str(current_time), Setting.key == "notify",
                                     Setting.enabled.is_(True))
    for setting in to_notify:
        if setting.enabled:
            # Check if user is missing happiness entries:
            entries = happiness_dao.get_happiness_by_timestamp(start=last_week, end=yesterday, user_id=setting.user_id)
            if len(entries) < 6:
                # They are missing an entry, and we are guaranteed to send an email which is expensive
                # Therefore we queue another job to redis
                app.queue.enqueue("jobs.jobs.send_notification_email", setting.user_id)


def test_job():
    print("Job running")
