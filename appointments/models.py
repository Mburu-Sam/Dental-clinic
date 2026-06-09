from django.contrib.auth.models import User
from django.db import models


class Doctor(models.Model):
    name           = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    phone          = models.CharField(max_length=20)
    bio            = models.TextField(blank=True)
    photo          = models.ImageField(upload_to='doctors/', blank=True, null=True)

    @property
    def display_name(self):
        clean_name = self.name.strip()
        if clean_name.lower().startswith('dr.') or clean_name.lower().startswith('dr '):
            return clean_name
        return f'Dr. {clean_name}'

    def __str__(self):
        return f"{self.display_name} — {self.specialization}"


class DoctorSchedule(models.Model):
    """Defines which days of the week and times a doctor is available."""

    DAYS = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    DURATIONS = [
        (30,  '30 minutes'),
        (60,  '1 hour'),
        (90,  '1.5 hours'),
        (120, '2 hours'),
    ]

    doctor        = models.ForeignKey(Doctor, on_delete=models.CASCADE,
                                      related_name='schedules')
    day_of_week   = models.IntegerField(choices=DAYS)
    start_time    = models.TimeField(help_text='e.g. 08:00')
    end_time      = models.TimeField(help_text='e.g. 17:00')
    slot_duration = models.IntegerField(choices=DURATIONS, default=60,
                                        help_text='Duration per appointment slot')
    is_active     = models.BooleanField(default=True,
                                        help_text='Uncheck to temporarily disable this schedule')

    class Meta:
        unique_together = ['doctor', 'day_of_week', 'start_time']
        ordering        = ['day_of_week', 'start_time']

    def __str__(self):
        return (f"Dr. {self.doctor.name} — "
                f"{self.get_day_of_week_display()} "
                f"{self.start_time.strftime('%H:%M')}–{self.end_time.strftime('%H:%M')}")


class Service(models.Model):
    name        = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=120, blank=True,
                                   help_text='Font Awesome icon class, e.g. fa-tooth')
    order       = models.IntegerField(default=0,
                                      help_text='Lower numbers appear first')
    is_active   = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    doctor     = models.ForeignKey(Doctor, on_delete=models.CASCADE,
                                   related_name='slots')
    date       = models.DateField()
    start_time = models.TimeField()
    is_booked  = models.BooleanField(default=False)

    class Meta:
        ordering            = ['date', 'start_time']
        unique_together     = ['doctor', 'date', 'start_time']

    def __str__(self):
        return f"{self.doctor.name} | {self.date} {self.start_time}"


class Appointment(models.Model):
    STATUS = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    patient   = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='appointments')
    slot      = models.OneToOneField(TimeSlot, on_delete=models.CASCADE,
                                     related_name='appointment')
    reason    = models.TextField(blank=True)
    status    = models.CharField(max_length=20, choices=STATUS, default='pending')
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-booked_at']

    def __str__(self):
        return (f"{self.patient.get_full_name() or self.patient.username} → "
                f"Dr. {self.slot.doctor.name} on {self.slot.date}")


class ContactMessage(models.Model):
    full_name  = models.CharField(max_length=150)
    email      = models.EmailField(blank=True)
    phone      = models.CharField(max_length=20)
    services   = models.TextField(blank=True)
    message    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read    = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.full_name} — {self.created_at.date()}"


