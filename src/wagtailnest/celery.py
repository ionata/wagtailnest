"""Bootstrap celery with Django's config"""
import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core_webapp_settings')
app = Celery(settings.CELERY_APP_NAME)
app.config_from_object('django.conf:settings')
