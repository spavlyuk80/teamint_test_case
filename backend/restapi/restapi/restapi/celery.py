import os
from celery import Celery
from celery.schedules import crontab
from users.tasks import enrich_multiple

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restapi.settings')

app = Celery('restapi')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, test.s(), name='add every 10')
    sender.add_periodic_task(crontab(minute="0", hour="0-23"),
                             enrich_multiple.s(), name='enrich empty')


@app.task
def test():
    print(">>>>>>>>>>>> TEST <<<<<<<<<<<<<<")