from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test email configuration'

    def add_arguments(self, parser):
        parser.add_argument('recipient_email', type=str, help='Email to send test message to')

    def handle(self, *args, **options):
        recipient = options['recipient_email']
        
        try:
            send_mail(
                subject='Test Email from Clinic System',
                message='If you see this, email is working!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Test email sent to {recipient}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Email failed: {str(e)}')
            )