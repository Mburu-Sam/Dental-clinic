from celery import shared_task
from .utils.email_service import KaratinaEmailService
   
@shared_task
def send_daily_reminders():
       """Send reminders for appointments tomorrow."""
       result = KaratinaEmailService.send_bulk_reminders()
       return f"Sent {result['sent']} reminders, skipped {result['skipped']}"