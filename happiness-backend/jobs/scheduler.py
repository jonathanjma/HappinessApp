import redis
from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue

from jobs.jobs import clear_exported_happiness, clean_tokens

"""
scheduler.py is the publisher responsible for publishing jobs to the redis db. 
https://devcenter.heroku.com/articles/clock-processes-python
"""


def init_app(app):
    sched = BlockingScheduler()

    redis_url = app.config['REDISCLOUD_URL']

    conn = redis.from_url(redis_url)
    q = Queue(connection=conn)

    @sched.scheduled_job('interval', hours=1)
    def scheduled_clear_exported_happiness():
        q.enqueue(clear_exported_happiness)

    @sched.scheduled_job('interval', hours=12)
    def scheduled_clean_tokens():
        q.enqueue(clean_tokens)

    # edit the parameters of the decorator to change scheduling
    # see https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html#module-apscheduler.triggers.cron
    @sched.scheduled_job('cron', minute="0,30")
    def scheduled_notify_emails():
        # TODO
        pass

    def scheduler_test():
        print("Scheduler running")

    @sched.scheduled_job('interval', seconds=1)
    def scheduled_test_scheduler():
        q.enqueue(scheduler_test)

    sched.start()
