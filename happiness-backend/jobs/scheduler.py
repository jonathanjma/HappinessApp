import os

import redis
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from rq import Queue

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

sched = BlockingScheduler()

load_dotenv()
redis_url = os.getenv('REDISCLOUD_URL')

conn = redis.from_url(redis_url)
q = Queue('happiness-backend-jobs', connection=conn)


@sched.scheduled_job('interval', days=1)
def scheduled_clear_exported_happiness():
    q.enqueue("jobs.jobs.clear_exported_happiness")


@sched.scheduled_job('interval', days=1)
def scheduled_clean_tokens():
    q.enqueue("jobs.jobs.clean_tokens")


@sched.scheduled_job('cron', minute="0,30")
def scheduled_queue_send_notification_emails():
    q.enqueue("jobs.jobs.queue_send_notification_emails")


sched.start()
