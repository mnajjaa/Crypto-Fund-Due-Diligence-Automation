import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DueDiligence.settings')

app = Celery('DueDiligence')

# Using a string here means the worker does not have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related config keys
#   should have a `CELERY_` prefix in settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps
app.autodiscover_tasks()
from celery import shared_task
from data.tasks import fetch_and_process_cryptos
# myproject/celery.py
from celery.schedules import schedule

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # run fetch_and_process_cryptos every 15 seconds
    sender.add_periodic_task(60.0, fetch_and_process_cryptos.s())
