import os

import redis
from rq import Worker, Queue

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISCLOUD_URL')

conn = redis.from_url(redis_url)

"""
worker.py listens for and processes all jobs that are pushed to the redis db. 
"""

if __name__ == '__main__':
    worker = Worker(map(Queue, listen), connection=conn)
    worker.work()
