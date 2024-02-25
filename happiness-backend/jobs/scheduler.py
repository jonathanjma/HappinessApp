from apscheduler.schedulers.background import BackgroundScheduler
from colorama import Fore, Style

"""
scheduler.py is the publisher responsible for publishing jobs to the redis db. 
It is independent from the Flask application and can be deployed as a clock in the Procfile.
See:
https://devcenter.heroku.com/articles/clock-processes-python

To find ways to schedule jobs effectively, see:
Cron jobs:
https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html
Interval jobs:
https://apscheduler.readthedocs.io/en/3.x/modules/triggers/interval.html
"""

scheduler_color = Fore.CYAN
RUN_SCHEDULER = True


# Run scheduler on separate thread in main server to avoid Heroku fees
# When testing, multiple schedulers may be created.
# This is because the production server has restarts.
# Use the terminal option `--no-reload` to fix this.
def init_app(app):
    sched = BackgroundScheduler()

    q = app.job_queue

    @sched.scheduled_job('interval', days=1)
    def scheduled_clear_exported_happiness():
        scheduler_log("Queuing job for exporting happiness")
        q.enqueue("jobs.jobs.clear_exported_happiness")

    @sched.scheduled_job('interval', days=1)
    def scheduled_clean_tokens():
        scheduler_log("Queuing job for cleaning tokens")
        q.enqueue("jobs.jobs.clean_tokens")

    @sched.scheduled_job('cron', minute="0,30")
    def scheduled_queue_send_notification_emails():
        scheduler_log("Queuing job for sending notification emails")
        q.enqueue("jobs.jobs.queue_send_notification_emails")

    if RUN_SCHEDULER:
        scheduler_log("Starting scheduler")
        sched.start()


def scheduler_log(text: str):
    print(scheduler_color + text + Style.RESET_ALL)
