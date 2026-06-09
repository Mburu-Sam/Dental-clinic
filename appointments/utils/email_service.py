# appointments/utils/email_service.py - CORRECTED VERSION
"""
Enhanced email service for Karatina Dental Clinic
Sends HTML emails for appointment confirmations, approvals, and reminders
Uses correct template paths for your folder structure: templates/appointments/emails/
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class KaratinaEmailService:
    """Handle all email operations for Karatina Dental Clinic"""

    CLINIC_NAME = "Karatina Dental Clinic"
    CLINIC_LOCATION = "Karatina, Nyeri County, Kenya"
    CLINIC_PHONE = "+254 (748) 681-792"  # Update with your actual phone
    CLINIC_EMAIL = settings.DEFAULT_FROM_EMAIL

    @staticmethod
    def _render_email(template_name, context, fallback_plain):
        try:
            html_message = render_to_string(template_name, context)
        except Exception as exc:
            logger.warning(
                f"Email template '{template_name}' could not be rendered: {exc}"
            )
            html_message = f"<pre>{fallback_plain}</pre>"
        plain_message = strip_tags(html_message)
        return html_message, plain_message

    @staticmethod
    def send_booking_confirmation(user, slot):
        """
        Send appointment booking confirmation email to patient.
        Called after patient books an appointment.
        """
        recipient = getattr(user, 'email', None)
        if not recipient:
            logger.warning(f"User {user.username} has no email address")
            return False

        patient_name = user.get_full_name() or user.username
        doctor_name = slot.doctor.display_name
        appointment_date = slot.date.strftime('%A, %d %B %Y')
        appointment_time = slot.start_time.strftime('%I:%M %p')

        context = {
            'patient_name': patient_name,
            'doctor_name': doctor_name,
            'appointment_date': appointment_date,
            'appointment_time': appointment_time,
            'clinic_name': KaratinaEmailService.CLINIC_NAME,
            'clinic_location': KaratinaEmailService.CLINIC_LOCATION,
            'clinic_phone': KaratinaEmailService.CLINIC_PHONE,
            'clinic_email': KaratinaEmailService.CLINIC_EMAIL,
            'doctor_specialization': slot.doctor.specialization,
        }

        try:
            html_message, plain_message = KaratinaEmailService._render_email(
                'appointments/emails/appointment_booking_confirmation.html',
                context,
                (
                    f'Dear {patient_name},\n\n'
                    f'Thank you for booking an appointment with {KaratinaEmailService.CLINIC_NAME}.\n\n'
                    f'Doctor: {doctor_name} ({slot.doctor.specialization})\n'
                    f'Date: {appointment_date}\n'
                    f'Time: {appointment_time}\n'
                    f'Location: {KaratinaEmailService.CLINIC_LOCATION}\n\n'
                    f'We will send a reminder email 24 hours before your appointment.\n\n'
                    f'Best regards,\n{KaratinaEmailService.CLINIC_NAME}'
                )
            )
            subject = f'Appointment Booking Confirmation — {KaratinaEmailService.CLINIC_NAME}'

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
            )
            email.attach_alternative(html_message, 'text/html')
            email.send(fail_silently=False)

            logger.info(f"Booking confirmation email sent to {recipient} for appointment on {appointment_date}")
            return True

        except Exception as e:
            logger.error(f"Failed to send booking confirmation email to {recipient}: {str(e)}")
            return False

    @staticmethod
    def send_approval_notification(user, slot):
        """
        Send appointment approval email to patient.
        Called when admin confirms a pending appointment.
        """
        recipient = getattr(user, 'email', None)
        if not recipient:
            logger.warning(f"User {user.username} has no email address")
            return False

        patient_name = user.get_full_name() or user.username
        doctor_name = slot.doctor.display_name
        appointment_date = slot.date.strftime('%A, %d %B %Y')
        appointment_time = slot.start_time.strftime('%I:%M %p')
        doctor_specialization = slot.doctor.specialization

        context = {
            'patient_name': patient_name,
            'doctor_name': doctor_name,
            'doctor_specialization': doctor_specialization,
            'appointment_date': appointment_date,
            'appointment_time': appointment_time,
            'clinic_name': KaratinaEmailService.CLINIC_NAME,
            'clinic_location': KaratinaEmailService.CLINIC_LOCATION,
            'clinic_phone': KaratinaEmailService.CLINIC_PHONE,
            'clinic_email': KaratinaEmailService.CLINIC_EMAIL,
        }

        try:
            html_message, plain_message = KaratinaEmailService._render_email(
                'appointments/emails/appointment_approval.html',
                context,
                (
                    f'Dear {patient_name},\n\n'
                    f'Your appointment has been approved.\n\n'
                    f'Doctor: {doctor_name} ({doctor_specialization})\n'
                    f'Date: {appointment_date}\n'
                    f'Time: {appointment_time}\n'
                    f'Location: {KaratinaEmailService.CLINIC_LOCATION}\n\n'
                    f'Please arrive 10 minutes early.\n\n'
                    f'Thank you,\n{KaratinaEmailService.CLINIC_NAME}'
                )
            )
            subject = f'✅ Appointment Approved — {KaratinaEmailService.CLINIC_NAME}'

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
            )
            email.attach_alternative(html_message, 'text/html')
            email.send(fail_silently=False)

            logger.info(f"Approval notification email sent to {recipient} for appointment on {appointment_date}")
            return True

        except Exception as e:
            logger.error(f"Failed to send approval notification email to {recipient}: {str(e)}")
            return False

    @staticmethod
    def send_reminder(user, slot):
        """
        Send appointment reminder email to patient.
        Called 24 hours before appointment (can be automated).
        """
        recipient = getattr(user, 'email', None)
        if not recipient:
            logger.warning(f"User {user.username} has no email address")
            return False

        patient_name = user.get_full_name() or user.username
        doctor_name = slot.doctor.display_name
        appointment_date = slot.date.strftime('%A, %d %B %Y')
        appointment_time = slot.start_time.strftime('%I:%M %p')

        context = {
            'patient_name': patient_name,
            'doctor_name': doctor_name,
            'appointment_date': appointment_date,
            'appointment_time': appointment_time,
            'clinic_name': KaratinaEmailService.CLINIC_NAME,
            'clinic_location': KaratinaEmailService.CLINIC_LOCATION,
            'clinic_phone': KaratinaEmailService.CLINIC_PHONE,
            'clinic_email': KaratinaEmailService.CLINIC_EMAIL,
        }

        try:
            html_message, plain_message = KaratinaEmailService._render_email(
                'appointments/emails/appointment_reminder.html',
                context,
                (
                    f'Dear {patient_name},\n\n'
                    f'This is a reminder for your appointment tomorrow.\n\n'
                    f'Doctor: {doctor_name}\n'
                    f'Date: {appointment_date}\n'
                    f'Time: {appointment_time}\n'
                    f'Location: {KaratinaEmailService.CLINIC_LOCATION}\n\n'
                    f'We look forward to seeing you.\n\n'
                    f'Best regards,\n{KaratinaEmailService.CLINIC_NAME}\n{KaratinaEmailService.CLINIC_PHONE}'
                )
            )
            subject = f'Reminder: Your Appointment Tomorrow at {KaratinaEmailService.CLINIC_NAME}'

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
            )
            email.attach_alternative(html_message, 'text/html')
            email.send(fail_silently=False)

            logger.info(f"Reminder email sent to {recipient} for appointment on {appointment_date}")
            return True

        except Exception as e:
            logger.error(f"Failed to send reminder email to {recipient}: {str(e)}")
            return False

    @staticmethod
    def send_cancellation_notification(user, slot, reason=None):
        """
        Send appointment cancellation notification email to patient.
        Called when appointment is cancelled (by patient or admin).
        """
        recipient = getattr(user, 'email', None)
        if not recipient:
            logger.warning(f"User {user.username} has no email address")
            return False

        patient_name = user.get_full_name() or user.username
        doctor_name = slot.doctor.display_name
        appointment_date = slot.date.strftime('%A, %d %B %Y')
        appointment_time = slot.start_time.strftime('%I:%M %p')

        context = {
            'patient_name': patient_name,
            'doctor_name': doctor_name,
            'appointment_date': appointment_date,
            'appointment_time': appointment_time,
            'cancellation_reason': reason or 'No reason provided',
            'clinic_name': KaratinaEmailService.CLINIC_NAME,
            'clinic_location': KaratinaEmailService.CLINIC_LOCATION,
            'clinic_phone': KaratinaEmailService.CLINIC_PHONE,
            'clinic_email': KaratinaEmailService.CLINIC_EMAIL,
        }

        try:
            html_message, plain_message = KaratinaEmailService._render_email(
                'appointments/emails/appointment_cancellation.html',
                context,
                (
                    f'Dear {patient_name},\n\n'
                    f'Your appointment has been cancelled.\n\n'
                    f'Doctor: {doctor_name}\n'
                    f'Date: {appointment_date}\n'
                    f'Time: {appointment_time}\n\n'
                    f'Cancellation reason: {context["cancellation_reason"]}\n\n'
                    f'Thank you,\n{KaratinaEmailService.CLINIC_NAME}'
                )
            )
            subject = f'Appointment Cancelled — {KaratinaEmailService.CLINIC_NAME}'

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
            )
            email.attach_alternative(html_message, 'text/html')
            email.send(fail_silently=False)

            logger.info(f"Cancellation notification email sent to {recipient}")
            return True

        except Exception as e:
            logger.error(f"Failed to send cancellation notification email to {recipient}: {str(e)}")
            return False

    @staticmethod
    def send_bulk_reminders():
        """
        Send reminders for all appointments tomorrow.
        Useful for scheduled tasks (Celery, cron jobs, management commands).
        """
        from datetime import date, timedelta
        from appointments.models import Appointment

        tomorrow = date.today() + timedelta(days=1)
        appointments = Appointment.objects.filter(
            slot__date=tomorrow,
            status__in=['pending', 'confirmed'],
        ).select_related('patient', 'slot__doctor')

        sent = 0
        skipped = 0

        for appt in appointments:
            if KaratinaEmailService.send_reminder(appt.patient, appt.slot):
                sent += 1
            else:
                skipped += 1

        logger.info(f"Bulk reminder: {sent} emails sent, {skipped} skipped")
        return {'sent': sent, 'skipped': skipped}