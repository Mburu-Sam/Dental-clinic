from django.core.management.base import BaseCommand
from appointments.utils.email_service import ClinicEmailService


class Command(BaseCommand):
    help = 'Send appointment reminder emails'

    def handle(self, *args, **options):
        count = ClinicEmailService.send_bulk_reminders()
        self.stdout.write(
            self.style.SUCCESS(f'✓ Sent {count} reminder emails')
        )