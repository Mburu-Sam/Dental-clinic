import os
from celery import Celery
from celery.schedules import crontab
   
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
   
app = Celery('clinic_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
   
app.conf.beat_schedule = {
       'send-appointment-reminders': {
           'task': 'appointments.tasks.send_daily_reminders',
           'schedule': crontab(hour=9, minute=0),  # 9 AM daily
       },
   }