from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from datetime import date, timedelta, time, datetime
from .models import Doctor, DoctorSchedule, TimeSlot, Appointment, ContactMessage


class DoctorScheduleInline(admin.TabularInline):
    model         = DoctorSchedule
    extra         = 1
    fields        = ('day_of_week', 'start_time', 'end_time', 'slot_duration', 'is_active')
    ordering      = ('day_of_week', 'start_time')


class TimeSlotInline(admin.TabularInline):
    model         = TimeSlot
    extra         = 1
    fields        = ('date', 'start_time', 'is_booked')
    ordering      = ('date', 'start_time')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display  = ['name', 'specialization', 'phone', 'schedule_summary']
    search_fields = ['name', 'specialization']
    ordering      = ['name']
    inlines       = [DoctorScheduleInline, TimeSlotInline]
    actions       = ['generate_slots_2_weeks', 'generate_slots_4_weeks', 'clear_future_empty_slots']

    def schedule_summary(self, obj):
        schedules = obj.schedules.filter(is_active=True)
        if not schedules:
            return format_html('<span style="color:#dc3545;">{}</span>', 'No schedule set')
        days = [s.get_day_of_week_display() for s in schedules]
        return format_html('<span style="color:#009688;">{}</span>', ', '.join(days))
    schedule_summary.short_description = 'Available Days'

    @admin.action(description='Generate slots — next 2 weeks')
    def generate_slots_2_weeks(self, request, queryset):
        count = _generate_slots_for_doctors(queryset, weeks=2)
        self.message_user(request, f'{count} new time slots generated for next 2 weeks.', messages.SUCCESS)

    @admin.action(description='Generate slots — next 4 weeks')
    def generate_slots_4_weeks(self, request, queryset):
        count = _generate_slots_for_doctors(queryset, weeks=4)
        self.message_user(request, f'{count} new time slots generated for next 4 weeks.', messages.SUCCESS)

    @admin.action(description='Clear future unbooked slots')
    def clear_future_empty_slots(self, request, queryset):
        deleted = TimeSlot.objects.filter(doctor__in=queryset, date__gte=date.today(), is_booked=False).delete()
        self.message_user(request, f'{deleted[0]} unbooked future slots removed.', messages.WARNING)


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display  = ['doctor', 'day_badge', 'start_time', 'end_time', 'slot_duration', 'slots_per_day', 'is_active']
    list_filter   = ['doctor', 'day_of_week', 'is_active']
    list_editable = ['is_active']
    ordering      = ['doctor', 'day_of_week', 'start_time']
    actions       = ['generate_slots_2_weeks', 'generate_slots_4_weeks', 'activate_schedules', 'deactivate_schedules']

    def day_badge(self, obj):
        colours = {0:'#3f51b5',1:'#009688',2:'#ff5722',3:'#795548',4:'#607d8b',5:'#e91e63',6:'#9c27b0'}
        col = colours.get(obj.day_of_week, '#333')
        return format_html('<span style="background:{};color:#fff;padding:2px 10px;border-radius:12px;font-size:12px;">{}</span>', col, obj.get_day_of_week_display())
    day_badge.short_description = 'Day'

    def slots_per_day(self, obj):
        start = datetime.combine(date.today(), obj.start_time)
        end   = datetime.combine(date.today(), obj.end_time)
        mins  = int((end - start).total_seconds() / 60)
        count = max(0, mins // obj.slot_duration)
        return format_html('<span style="color:#009688;font-weight:700;">{} slots</span>', count)
    slots_per_day.short_description = 'Slots/Day'

    @admin.action(description='Generate slots — next 2 weeks')
    def generate_slots_2_weeks(self, request, queryset):
        doctors = Doctor.objects.filter(schedules__in=queryset).distinct()
        count = _generate_slots_for_doctors(doctors, weeks=2)
        self.message_user(request, f'{count} new slots generated.', messages.SUCCESS)

    @admin.action(description='Generate slots — next 4 weeks')
    def generate_slots_4_weeks(self, request, queryset):
        doctors = Doctor.objects.filter(schedules__in=queryset).distinct()
        count = _generate_slots_for_doctors(doctors, weeks=4)
        self.message_user(request, f'{count} new slots generated.', messages.SUCCESS)

    @admin.action(description='Activate selected schedules')
    def activate_schedules(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, 'Schedules activated.', messages.SUCCESS)

    @admin.action(description='Deactivate selected schedules')
    def deactivate_schedules(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, 'Schedules deactivated.', messages.WARNING)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display   = ['doctor', 'date', 'day_name', 'start_time', 'is_booked']
    list_filter    = ['doctor', 'date', 'is_booked']
    ordering       = ['date', 'start_time']
    list_editable  = ['is_booked']
    date_hierarchy = 'date'

    def day_name(self, obj):
        return obj.date.strftime('%A')
    day_name.short_description = 'Day'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display   = ['patient', 'slot', 'status', 'booked_at']
    list_filter    = ['status', 'slot__doctor']
    search_fields  = ['patient__username', 'patient__first_name', 'patient__last_name']
    list_editable  = ['status']
    readonly_fields = ['booked_at']
    ordering        = ['-booked_at']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ['full_name', 'phone', 'email', 'created_at', 'is_read']
    list_filter   = ['is_read']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
    ordering        = ['-created_at']


def _generate_slots_for_doctors(doctors, weeks=2):
    created_count = 0
    today    = date.today()
    end_date = today + timedelta(weeks=weeks)
    current  = today
    while current <= end_date:
        weekday = current.weekday()
        for doctor in doctors:
            for schedule in doctor.schedules.filter(day_of_week=weekday, is_active=True):
                slot_start = datetime.combine(current, schedule.start_time)
                slot_end   = datetime.combine(current, schedule.end_time)
                while slot_start < slot_end:
                    _, created = TimeSlot.objects.get_or_create(
                        doctor=doctor, date=current, start_time=slot_start.time())
                    if created:
                        created_count += 1
                    slot_start += timedelta(minutes=schedule.slot_duration)
        current += timedelta(days=1)
    return created_count
