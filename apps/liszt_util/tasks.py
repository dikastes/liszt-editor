from celery import shared_task
import time

@shared_task(name='liszt_util.tasks.add_test')
def add_test(x,y):
    time.sleep(10)
    return x+y