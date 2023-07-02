import datetime
import os

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()


@sched.scheduled_job('interval', hours=1)
def clear_exports():
    # TODO use RQ to run jobs, don't run directly in clock.py
    # https://devcenter.heroku.com/articles/python-rq
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

    folder_path = "export"
    minutes5ago = (datetime.datetime.now() - datetime.timedelta(minutes=5))
    delete_files_older_than(folder_path, minutes5ago)


sched.start()
