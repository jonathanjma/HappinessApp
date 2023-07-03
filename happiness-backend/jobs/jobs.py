import datetime
import os

# from api.models import Token

"""
jobs.py contains all scheduled jobs that will be queued by scheduler.py
"""


def clear_exported_happiness():
    """
    Deletes all files in the `export` folder that are older than 1 hour.
    """

    def delete_files_older_than(m_folder_path, threshold_time):
        for root, dirs, files in os.walk(m_folder_path):
            for file in files:
                print("file exists")
                file_path = os.path.join(root, file)
                created_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                print(f"created time: {created_time}")

                if created_time < threshold_time:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")

    folder_path = "../export"
    minutes5ago = (datetime.datetime.now() - datetime.timedelta(hours=1))
    delete_files_older_than(folder_path, minutes5ago)


def clean_tokens():
    """
    Deletes all expired tokens
    """
    # Token.clean()
    pass


def send_notification_email(email):
    """
    Sends a happiness app reminder notification email to the given email.
    """
    # TODO
    pass
