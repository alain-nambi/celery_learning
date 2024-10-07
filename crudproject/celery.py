from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


# Set the defauld Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudproject.settings')

# Create a new Celery instance
app = Celery('crudproject')

# Configure Celery settings from Django settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs
app.autodiscover_tasks()
