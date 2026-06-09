from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from appointments.models import Appointment
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Send reminder emails to patients with appointments tomorrow'

    def handle(self, *args, **kwargs):
        tomorrow = date.today() + timedelta(days=1)

        # Get all confirmed or pending appointments for tomorrow
        appointments = Appointment.objects.filter(
            slot__date   = tomorrow,
            status__in   = ['pending', 'confirmed'],
        ).select_related('patient', 'slot__doctor')

        if not appointments.exists():
            self.stdout.write('No appointments tomorrow. No reminders sent.')
            return

        sent  = 0
        skipped = 0

        for appt in appointments:
            patient = appt.patient
            slot    = appt.slot

            # Skip if patient has no email
            if not patient.email:
                skipped += 1
                continue

            name    = patient.get_full_name() or patient.username
            doctor  = slot.doctor.display_name
            date_str= slot.date.strftime('%A, %d %B %Y')
            time_str= slot.start_time.strftime('%I:%M %p')

            try:
                send_mail(
                    subject = 'Appointment Reminder — Karatina Dental Clinic',
                    message = f"""Dear {name},

            This is a friendly reminder that you have a dental appointment TOMORROW.

            Dentist : {doctor}
            Date    : {date_str}
            Time    : {time_str}
            Venue   : Karatina Dental Clinic, Karatina Plaza, Karatina Town

            Please arrive 10 minutes early.
            If you need to cancel, log in to your account at:
            http://127.0.0.1:8000/mine/

            Thank you,
            Karatina Dental Clinic
            Tel: +254 748 681 792
            """,
                    from_email     = settings.DEFAULT_FROM_EMAIL,
                    recipient_list = [patient.email],
                    fail_silently  = False,
                )
                sent += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Reminder sent → {name} ({patient.email}) '
                        f'— {doctor} at {time_str}'))

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Failed for {name}: {e}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone. {sent} reminders sent, {skipped} skipped (no email).'))