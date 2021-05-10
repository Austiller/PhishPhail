import os

from celery import Celery

# set the default Django settings environmental variable for celery command line
# Not needed
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phishFail.settings')

# Must be created before app instances are started, hence the call by __init__
app = Celery('phishFail')

# Allows for configuration of celery via django settings file
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

#  debug_task example is a task that dumps its own request information.
#  This is using the new bind=True task option introduced in Celery 3.1 to easily refer to the current task instance.
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

if __name__ == '__main__':
    app.start()