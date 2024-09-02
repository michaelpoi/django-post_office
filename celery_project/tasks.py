import random

from celery import shared_task

@shared_task
def sample(*args, **kwargs):
    print(f"HELLO {random.randint(1,100)}")