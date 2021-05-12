from .celery import app

from modeler import models


from django_celery_beat.models import PeriodicTask, IntervalSchedule

schedule, created = IntervalSchedule.objects.get_or_create( every=60, period=IntervalSchedule.SECONDS,)

periodic_task = PeriodicTask(interval=schedule,name="match_fqdn",task='fqdn.tasks.fetch_found_fqdn')