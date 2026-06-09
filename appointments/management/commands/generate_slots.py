from django.core.management.base import BaseCommand
from appointments.models import Doctor, DoctorSchedule, TimeSlot
from datetime import date, timedelta, datetime


class Command(BaseCommand):
    help = 'Generate time slots from doctor schedules'

    def add_arguments(self, parser):
        parser.add_argument('--weeks', type=int, default=2,
                            help='How many weeks ahead to generate slots (default: 2)')
        parser.add_argument('--doctor', type=int, default=None,
                            help='Doctor ID (optional — leave blank for all doctors)')

    def handle(self, *args, **options):
        weeks     = options['weeks']
        doctor_id = options['doctor']

        doctors = Doctor.objects.all()
        if doctor_id:
            doctors = doctors.filter(id=doctor_id)

        if not doctors.exists():
            self.stdout.write(self.style.ERROR('No doctors found.'))
            return

        today    = date.today()
        end_date = today + timedelta(weeks=weeks)
        current  = today
        total    = 0

        self.stdout.write(f'Generating slots from {today} to {end_date}...\n')

        while current <= end_date:
            weekday = current.weekday()  # 0=Mon … 6=Sun
            for doctor in doctors:
                schedules = doctor.schedules.filter(
                    day_of_week=weekday, is_active=True)
                for schedule in schedules:
                    slot_start = datetime.combine(current, schedule.start_time)
                    slot_end   = datetime.combine(current, schedule.end_time)
                    while slot_start < slot_end:
                        _, created = TimeSlot.objects.get_or_create(
                            doctor     = doctor,
                            date       = current,
                            start_time = slot_start.time(),
                        )
                        if created:
                            total += 1
                        slot_start += timedelta(minutes=schedule.slot_duration)
            current += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(
            f'✅ Done! {total} new time slots created across {doctors.count()} doctor(s).'))
