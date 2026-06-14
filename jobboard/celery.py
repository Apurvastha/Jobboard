import os

from celery import Celery

# tell Celery which django settings to use
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobboard.settings")

# create Celery application
app = Celery("jobboard")

# read config from Django settings
# all Celery settings in settings.py starts with CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# auto-discover tasks in all installed apps
# looks for tasks.py in every loop
app.autodiscover_tasks()
