import os
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

    def delete_files_older_than(m_folder_path, threshold_time):
        for root, dirs, files in os.walk(m_folder_path):
            for file in files:
                print("file exists")
                file_path = os.path.join(root, file)
                created_time = datetime.fromtimestamp(os.path.getctime(file_path))
                print(f"created time: {created_time}")

                if created_time < threshold_time:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")

    folder_path = "../export"
    minutes5ago = (datetime.now() - timedelta(hours=1))
    delete_files_older_than(folder_path, minutes5ago)


def clean_tokens():
    """
    Deletes all expired tokens
    """
    Token.clean()
    pass


def send_notification_emails(user_id):
    """
    Sends a happiness app reminder notification email to the given email.
    """
    user_to_send = users_dao.get_user_by_id(user_id)
    dates_should_be_present = [
        (datetime.now() - timedelta(days=i)).strftime("%m-%d-%Y") for i in range(1, 7)
    ]
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%m-%d-%Y")
    last_week = (datetime.now() - timedelta(days=6)).strftime("%m-%d-%Y")
    entries = happiness_dao.get_happiness_by_timestamp(start=last_week, end=yesterday, user_id=user_id)
    for e in entries:
        if e.timestamp in dates_should_be_present:
            dates_should_be_present.remove(e.timestamp)
    missing_dates_str = "\n".join(dates_should_be_present)

    send_email_helper(
        subject="Enter Your Happiness :)",
        sender="noreply@happinessapp.org",
        recipients=user_to_send.email,
        text_body=render_template('notify_happiness.txt', user=user_to_send, dates=missing_dates_str),
        html_body=render_template('notify_happiness.html', user=user_to_send, dates=missing_dates_str)
    )
    pass


def queue_send_notification_emails():
    """
    Adds all notification email requests to the redis queue
    """
    current_time = datetime.now().time()
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%m-%d-%Y")
    last_week = (datetime.now() - timedelta(days=6)).strftime("%m-%d-%Y")

    to_notify = Setting.query.filter(Setting.value == str(current_time))
    for setting in to_notify:
        if setting.enabled:
            # Check if user is missing happiness entries:
            entries = happiness_dao.get_happiness_by_timestamp(start=last_week, end=yesterday, user_id=setting.user_id)
            if len(entries) < 6:
                # They are missing an entry, and we are guaranteed to send an email which is expensive
                # Therefore we queue another job to redis
                app.queue.enqueue("jobs.jobs.send_notification_email", setting.user_id)
