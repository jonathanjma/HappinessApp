import os

import dotenv
import redis
from rq import Worker, Queue, Connection

"""
worker.py listens for and processes all jobs that are pushed to the redis db. 

This does not work on Windows! See https://python-rq.org/docs/#limitations

Source for general file logic: https://devcenter.heroku.com/articles/python-rq#create-a-worker
"""

listen = ['high', 'default', 'low']

# Since worker.py runs independently of the app we can't use the app config.
dotenv.load_dotenv()
redis_url = os.getenv('REDISCLOUD_URL')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
