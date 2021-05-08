
from celery import shared_task


# The @shared_task decorator lets you create tasks without having any concrete app instance:
@shared_task
def add(x, y):
    return x + y



