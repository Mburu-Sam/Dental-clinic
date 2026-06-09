from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from clinic_system.settings import is_invalid_smtp_password

from .models import Appointment, Doctor, TimeSlot


class EmailPasswordValidationTests(SimpleTestCase):
    def test_detects_placeholder_and_demo_passwords(self):
        self.assertTrue(is_invalid_smtp_password(''))
        self.assertTrue(is_invalid_smtp_password('your-16-char-app-password'))
        self.assertTrue(is_invalid_smtp_password('your-email@gmail.com'))
        self.assertTrue(is_invalid_smtp_password('changeme'))
        self.assertTrue(is_invalid_smtp_password('karatina1234clinic'))

    def test_accepts_realistic_app_password_like_values(self):
        self.assertFalse(is_invalid_smtp_password('abcd1234efgh5678'))
        self.assertFalse(is_invalid_smtp_password('16charappsecret!'))


class AdminCancellationTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='secret',
            is_staff=True,
            is_superuser=True,
        )
        self.patient = User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='secret',
        )
        doctor = Doctor.objects.create(
            name='Dr. Test',
            specialization='General Dentistry',
            phone='0712345678',
        )
        self.slot = TimeSlot.objects.create(
            doctor=doctor,
            date='2026-06-15',
            start_time='10:00:00',
            is_booked=True,
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            slot=self.slot,
            status='confirmed',
        )

    @patch('appointments.views.KaratinaEmailService.send_cancellation_notification', return_value=False)
    def test_admin_cancellation_saves_reason(self, _mock_send):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse('admin_cancel_appointment', args=[self.appointment.id]),
            {'cancellation_reason': 'Patient requested reschedule'},
        )

        self.assertEqual(response.status_code, 302)

        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'cancelled')
        self.assertEqual(self.appointment.reason, 'Patient requested reschedule')
        self.assertFalse(self.slot.refresh_from_db().is_booked)
