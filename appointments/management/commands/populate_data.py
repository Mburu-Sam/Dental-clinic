from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from appointments.models import Doctor, DoctorSchedule, TimeSlot, Service
from datetime import date, timedelta, datetime
from django.utils import timezone


class Command(BaseCommand):
    help = 'Populate database with sample data for Karatina Dental Clinic'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        # ── Superuser ──────────────────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin', email='admin@karatinadental.co.ke',
                password='admin1234', first_name='Clinic', last_name='Administrator')
            self.stdout.write(self.style.SUCCESS('✓ Admin created  →  admin / admin1234'))

        # ── Sample patients ────────────────────────────────────────────────
        for uname, email, first, last in [
            ('mary.wanjiku','mary@gmail.com','Mary','Wanjiku'),
            ('john.mwangi','john@gmail.com','John','Mwangi'),
            ('grace.njeri','grace@gmail.com','Grace','Njeri'),
        ]:
            if not User.objects.filter(username=uname).exists():
                User.objects.create_user(username=uname, email=email,
                    password='patient1234', first_name=first, last_name=last)
        self.stdout.write(self.style.SUCCESS('✓ Sample patients created  →  password: patient1234'))

        # ── Default services ───────────────────────────────────────────────
        services_data = [
            {
                'name': 'General Dentistry',
                'description': 'Routine checkups, fillings, extractions and general oral care.',
                'icon': 'fas fa-tooth',
                'order': 1,
            },
            {
                'name': 'Cosmetic Dentistry',
                'description': 'Teeth whitening, veneers and smile makeovers for a brighter smile.',
                'icon': 'fas fa-smile',
                'order': 2,
            },
            {
                'name': 'Pediatric Dentistry',
                'description': 'Gentle dental care for children using kid-friendly techniques.',
                'icon': 'fas fa-child',
                'order': 3,
            },
            {
                'name': 'Orthodontics',
                'description': 'Braces and aligners to straighten teeth and improve bite alignment.',
                'icon': 'fas fa-graduation-cap',
                'order': 4,
            },
            {
                'name': 'Dental Implants',
                'description': 'Long-term tooth replacement solutions with natural-looking results.',
                'icon': 'fas fa-tooth',
                'order': 5,
            },
            {
                'name': 'Teeth Cleaning',
                'description': 'Professional hygiene cleaning for healthy gums and fresher breath.',
                'icon': 'fas fa-brush',
                'order': 6,
            },
        ]

        created_count = 0
        for service in services_data:
            obj, created = Service.objects.get_or_create(
                name=service['name'],
                defaults={
                    'description': service['description'],
                    'icon': service['icon'],
                    'order': service['order'],
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f'✓ Default services created ({created_count})'))

        # ── Doctors with realistic schedules ───────────────────────────────
        doctors_data = [
            {
                'name': 'Dr. James Kamau',
                'spec': 'General Dentistry',
                'phone': '+254 711 000 001',
                'bio': 'Over 10 years of experience in general and restorative dentistry.',
                # Available Mon, Wed, Fri  8am-12pm  (60 min slots)
                'schedules': [
                    (0, '08:00', '12:00', 60),  # Monday
                    (2, '08:00', '12:00', 60),  # Wednesday
                    (4, '08:00', '13:00', 60),  # Friday
                ],
            },
            {
                'name': 'Dr. Amina Hassan',
                'spec': 'Cosmetic Dentistry',
                'phone': '+254 711 000 002',
                'bio': 'Specialist in teeth whitening, veneers and smile makeovers.',
                # Available Tue, Thu  10am-4pm  (60 min slots)
                'schedules': [
                    (1, '10:00', '16:00', 60),  # Tuesday
                    (3, '10:00', '16:00', 60),  # Thursday
                    (5, '09:00', '13:00', 60),  # Saturday
                ],
            },
            {
                'name': 'Dr. Peter Njoroge',
                'spec': 'Pediatric Dentistry',
                'phone': '+254 711 000 003',
                'bio': 'Dedicated to gentle dental care for children of all ages.',
                # Available Mon-Sat  14:00-17:00  (30 min slots)
                'schedules': [
                    (0, '14:00', '17:00', 30),  # Monday
                    (1, '14:00', '17:00', 30),  # Tuesday
                    (2, '14:00', '17:00', 30),  # Wednesday
                    (3, '14:00', '17:00', 30),  # Thursday
                    (4, '14:00', '17:00', 30),  # Friday
                ],
            },
        ]

        slot_total = 0
        for data in doctors_data:
            doc, _ = Doctor.objects.get_or_create(
                name=data['name'],
                defaults=dict(specialization=data['spec'],
                              phone=data['phone'], bio=data['bio']))

            for day, start, end, dur in data['schedules']:
                from datetime import time
                DoctorSchedule.objects.get_or_create(
                    doctor=doc, day_of_week=day,
                    start_time=time(*[int(x) for x in start.split(':')]),
                    defaults=dict(
                        end_time=time(*[int(x) for x in end.split(':')]),
                        slot_duration=dur, is_active=True))

            # Generate slots for next 3 weeks
            today    = date.today()
            end_date = today + timedelta(weeks=3)
            current  = today
            while current <= end_date:
                weekday = current.weekday()
                for sched in doc.schedules.filter(day_of_week=weekday, is_active=True):
                    slot_dt  = datetime.combine(current, sched.start_time)
                    slot_end = datetime.combine(current, sched.end_time)
                    while slot_dt < slot_end:
                        _, created = TimeSlot.objects.get_or_create(
                            doctor=doc, date=current, start_time=slot_dt.time())
                        if created:
                            slot_total += 1
                        slot_dt += timedelta(minutes=sched.slot_duration)
                current += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(f'✓ 3 doctors + schedules + {slot_total} slots created'))
        self.stdout.write(self.style.SUCCESS(
            '\n✅ Ready!\n'
            '   Admin    → http://127.0.0.1:8000/admin/         (admin / admin1234)\n'
            '   Patient  → mary.wanjiku / john.mwangi / grace.njeri  (patient1234)\n'
            '   Schedules→ http://127.0.0.1:8000/schedules/\n'
        ))
