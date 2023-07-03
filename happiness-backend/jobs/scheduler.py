import os

import redis
from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue

from jobs import clear_exported_happiness, clean_tokens

sched = BlockingScheduler()

redis_url = os.getenv('REDIS_URL')

conn = redis.from_url(redis_url)
q = Queue(connection=conn)


@sched.scheduled_job('interval', hours=1)
def scheduled_clear_exported_happiness():
    q.enqueue(clear_exported_happiness)


@sched.scheduled_job('interval', hours=12)
def scheduled_clean_tokens():
    q.enqueue(clean_tokens)


@sched.scheduled_job('cron', minute="0,30")
def scheduled_notify_emails():
    # TODO
    pass


sched.start()
