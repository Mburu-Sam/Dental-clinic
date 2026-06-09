from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.conf import settings
from datetime import date
from .models import Doctor, TimeSlot, Appointment, ContactMessage
from .services import load_services

# Import the new email service
from .utils.email_service import KaratinaEmailService


# ── Home ──────────────────────────────────────────────────────────────────────
def home(request):
    doctors = Doctor.objects.all()
    services = load_services()
    why_us = [
        ("Qualified & Experienced Dentists",
         "Our dental team delivers high-quality care using modern techniques and the latest equipment.",
         "fas fa-user-md"),
        ("Affordable Pricing",
         "We believe quality dental care should be accessible to everyone in Karatina and Nyeri County.",
         "fas fa-tag"),
        ("Modern Equipment",
         "We use up-to-date dental technology with strict sterilisation and infection control protocols.",
         "fas fa-microscope"),
        ("Comfortable Environment",
         "Our clinic is designed to make you feel calm and comfortable from the moment you walk in.",
         "fas fa-couch"),
    ]
    testimonials = [
        ("Mary Wanjiku",
         "The staff are so friendly and professional. Dr. Kamau made me feel completely at ease during my root canal. Excellent service!"),
        ("John Mwangi",
         "Very clean clinic, modern equipment and fair pricing. I brought my whole family here and we are all very happy with the results."),
        ("Grace Njeri",
         "I had my teeth whitened here and the results are amazing. Highly recommend Karatina Dental Clinic to everyone in Nyeri County!"),
    ]
    return render(request, 'home.html', {
        'doctors':      doctors,
        'services':     services,
        'why_us':       why_us,
        'testimonials': testimonials,
    })


# ── Book Appointment ──────────────────────────────────────────────────────────
@login_required
def book_appointment(request):
    doctors         = Doctor.objects.all()
    slots           = None
    selected_doctor = None

    if request.GET.get('doctor_id'):
        selected_doctor = get_object_or_404(Doctor, id=request.GET['doctor_id'])
        slots = TimeSlot.objects.filter(
            doctor    = selected_doctor,
            is_booked = False,
            date__gte = date.today()
        ).order_by('date', 'start_time')

    if request.method == 'POST':
        slot_id = request.POST.get('slot_id')
        slot    = get_object_or_404(TimeSlot, id=slot_id)

        # Guard 1 – already booked flag
        if slot.is_booked:
            messages.error(request,
                'Sorry, that slot was just taken. Please choose another time.')
            return redirect(request.get_full_path())

        # Guard 2 – DB duplicate
        if Appointment.objects.filter(slot=slot).exists():
            messages.error(request,
                'This slot is no longer available. Please select another.')
            return redirect(request.get_full_path())

        # Guard 3 – same patient, same doctor, same day
        if Appointment.objects.filter(
            patient       = request.user,
            slot__doctor  = slot.doctor,
            slot__date    = slot.date,
            status__in    = ['pending', 'confirmed']
        ).exists():
            messages.warning(request,
                'You already have an appointment with this dentist on that day.')
            return redirect('my_appointments')

        # Save appointment
        slot.is_booked = True
        slot.save()

        appt = Appointment.objects.create(
            patient = request.user,
            slot    = slot,
            reason  = request.POST.get('reason', ''),
            status  = 'pending',
        )

        # ✨ NEW: Send confirmation email using the new service
        email_sent = KaratinaEmailService.send_booking_confirmation(request.user, slot)
        
        if email_sent:
            messages.success(request,
                f'✅ Appointment request received for {slot.doctor.display_name} '
                f'on {slot.date} at {slot.start_time}. '
                f'A confirmation email has been sent to {request.user.email}.')
        else:
            messages.warning(request,
                f'✅ Appointment request received for {slot.doctor.display_name} '
                f'on {slot.date} at {slot.start_time}. '
                f'We could not send a confirmation email. Please check your account email.')
        
        return redirect('my_appointments')

    return render(request, 'appointments/book.html', {
        'doctors':         doctors,
        'slots':           slots,
        'selected_doctor': selected_doctor,
    })


def services_page(request):
    services = load_services()
    return render(request, 'services.html', {
        'services': services,
    })


# ── My Appointments ───────────────────────────────────────────────────────────
@login_required
def my_appointments(request):
    all_appts = Appointment.objects.filter(patient=request.user)
    pending   = all_appts.filter(status='pending').count()
    confirmed = all_appts.filter(status='confirmed').count()
    cancelled = all_appts.filter(status='cancelled').count()
    return render(request, 'appointments/my_appointments.html', {
        'appointments': all_appts,
        'total':        all_appts.count(),
        'pending':      pending,
        'confirmed':    confirmed,
        'cancelled':    cancelled,
    })


# ── Cancel Appointment ────────────────────────────────────────────────────────
@login_required
def cancel_appointment(request, appointment_id):
    appt = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    if appt.status in ['pending', 'confirmed']:
        # ✨ NEW: Send cancellation email before status change
        cancellation_reason = request.POST.get('cancellation_reason', '')
        email_sent = KaratinaEmailService.send_cancellation_notification(
            request.user, appt.slot, cancellation_reason
        )
        
        # Update appointment status
        appt.status          = 'cancelled'
        appt.slot.is_booked  = False
        appt.slot.save()
        appt.save()
        
        if email_sent:
            messages.success(request, '✅ Your appointment has been cancelled. A confirmation email has been sent.')
        else:
            messages.warning(request, '⚠️ Appointment cancelled, but confirmation email could not be sent.')
    else:
        messages.warning(request, 'This appointment cannot be cancelled.')
    
    return redirect('my_appointments')


# ── Admin Dashboard ───────────────────────────────────────────────────────────
@staff_member_required
def admin_dashboard(request):
    total     = Appointment.objects.count()
    pending   = Appointment.objects.filter(status='pending').count()
    confirmed = Appointment.objects.filter(status='confirmed').count()
    cancelled = Appointment.objects.filter(status='cancelled').count()
    recent    = Appointment.objects.select_related(
                    'patient', 'slot__doctor').order_by('-booked_at')[:15]
    doctors   = Doctor.objects.all()
    messages_count = ContactMessage.objects.filter(is_read=False).count()

    return render(request, 'appointments/admin_dashboard.html', {
        'total':          total,
        'pending':        pending,
        'confirmed':      confirmed,
        'cancelled':      cancelled,
        'recent':         recent,
        'doctors':        doctors,
        'messages_count': messages_count,
    })


# ── Admin: Confirm Appointment ────────────────────────────────────────────────
@staff_member_required
def confirm_appointment(request, appointment_id):
    appt = get_object_or_404(Appointment, id=appointment_id)
    previous_status = appt.status
    appt.status = 'confirmed'
    appt.save()

    # ✨ NEW: Send approval email using the new service
    email_sent = False
    if previous_status != 'confirmed':
        email_sent = KaratinaEmailService.send_approval_notification(appt.patient, appt.slot)

    if email_sent:
        messages.success(request,
            f'✅ Appointment for {appt.patient.username} confirmed. '
            f'Approval email sent to {appt.patient.email}.')
    else:
        messages.warning(request,
            f'Appointment for {appt.patient.username} confirmed. '
            f'(Email could not be sent - {appt.patient.email} may be invalid.)')
    
    return redirect('admin_dashboard')


# ── Admin: Cancel Any Appointment ────────────────────────────────────────────
@staff_member_required
def admin_cancel_appointment(request, appointment_id):
    appt = get_object_or_404(Appointment, id=appointment_id)
    
    # ✨ NEW: Send cancellation email before cancelling
    cancellation_reason = "Cancelled by clinic staff"
    email_sent = KaratinaEmailService.send_cancellation_notification(
        appt.patient, appt.slot, cancellation_reason
    )
    
    # Update appointment
    appt.status         = 'cancelled'
    appt.slot.is_booked = False
    appt.slot.save()
    appt.save()
    
    if email_sent:
        messages.success(request, 
            f'✅ Appointment cancelled. Patient notification email sent to {appt.patient.email}.')
    else:
        messages.warning(request, 
            'Appointment cancelled. (Patient notification email could not be sent.)')
    
    return redirect('admin_dashboard')


# ── Contact Page ──────────────────────────────────────────────────────────────
def contact(request):
    success = False

    if request.method == 'POST':
        full_name      = request.POST.get('full_name', '').strip()
        email          = request.POST.get('email', '').strip()
        phone          = request.POST.get('phone', '').strip()
        msg_text       = request.POST.get('message', '').strip()
        selected_svcs  = request.POST.getlist('services')

        if full_name and phone:
            ContactMessage.objects.create(
                full_name = full_name,
                email     = email,
                phone     = phone,
                services  = ', '.join(selected_svcs),
                message   = msg_text,
            )
            
            # Send notification to clinic
            from django.core.mail import send_mail
            send_mail(
                subject   = f'New Contact Message: {full_name}',
                message   = (
                    f'Name:     {full_name}\n'
                    f'Phone:    {phone}\n'
                    f'Email:    {email}\n'
                    f'Services: {", ".join(selected_svcs)}\n\n'
                    f'Message:\n{msg_text}'
                ),
                from_email        = settings.DEFAULT_FROM_EMAIL,
                recipient_list    = [settings.EMAIL_HOST_USER],
                fail_silently     = True,
            )
            success = True
            messages.success(request,
                'Thank you! Your message has been received. We will contact you shortly.')
        else:
            messages.error(request, 'Please fill in your name and phone number.')

    service_list = load_services()
    return render(request, 'contact.html', {
        'service_list': service_list,
        'success':      success,
    })


# ── Manage Doctor Schedules (Admin) ───────────────────────────────────────────
@staff_member_required
def manage_schedules(request):
    from .models import DoctorSchedule
    from .admin import _generate_slots_for_doctors
    from datetime import date, datetime

    doctors   = Doctor.objects.prefetch_related('schedules').all()
    generated = None

    if request.method == 'POST':
        action    = request.POST.get('action')
        doctor_id = request.POST.get('doctor_id')
        weeks     = int(request.POST.get('weeks', 2))

        selected = Doctor.objects.filter(id=doctor_id) if doctor_id else Doctor.objects.all()

        if action == 'generate':
            generated = _generate_slots_for_doctors(selected, weeks=weeks)
            messages.success(request,
                f'✅ {generated} new time slots generated for the next {weeks} weeks.')

        elif action == 'clear':
            deleted = TimeSlot.objects.filter(
                doctor__in=selected,
                date__gte=date.today(),
                is_booked=False
            ).delete()
            messages.warning(request,
                f'🗑 {deleted[0]} unbooked future slots removed.')

        elif action == 'add_slot':
            slot_doctor_id  = request.POST.get('slot_doctor_id')
            slot_date       = request.POST.get('slot_date')
            slot_start_time = request.POST.get('slot_start_time')

            if not slot_doctor_id or not slot_date or not slot_start_time:
                messages.error(request,
                    'Please select a doctor, date, and time for the slot.')
                return redirect('manage_schedules')

            selected_doctor = get_object_or_404(Doctor, id=slot_doctor_id)
            try:
                start_time = datetime.strptime(slot_start_time, '%H:%M').time()
                slot_day   = date.fromisoformat(slot_date)
            except ValueError:
                messages.error(request,
                    'Please enter a valid date and time for the slot.')
                return redirect('manage_schedules')

            slot, created = TimeSlot.objects.get_or_create(
                doctor     = selected_doctor,
                date       = slot_day,
                start_time = start_time,
            )

            if created:
                messages.success(request,
                    f'✅ New slot added for {selected_doctor.display_name} on {slot_day} at {slot_start_time}.')
            else:
                messages.warning(request,
                    f'⚠️ A slot already exists for {selected_doctor.display_name} on {slot_day} at {slot_start_time}.')

        return redirect('manage_schedules')

    # Build schedule summary for display
    day_names = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    schedule_data = []
    for doctor in doctors:
        active_schedules = doctor.schedules.filter(is_active=True).order_by('day_of_week')
        available_slots  = TimeSlot.objects.filter(
            doctor=doctor, date__gte=date.today(), is_booked=False).count()
        schedule_data.append({
            'doctor':    doctor,
            'schedules': active_schedules,
            'available': available_slots,
        })

    return render(request, 'appointments/manage_schedules.html', {
        'schedule_data': schedule_data,
        'doctors':       doctors,
        'day_names':     day_names,
    })


# ── Send Reminders (Admin) ────────────────────────────────────────────────────
@staff_member_required
def send_reminders_now(request):
    """Manually trigger reminder emails from the admin dashboard."""
    from datetime import date, timedelta

    tomorrow     = date.today() + timedelta(days=1)
    appointments = Appointment.objects.filter(
        slot__date = tomorrow,
        status__in = ['pending', 'confirmed'],
    ).select_related('patient', 'slot__doctor')

    # ✨ NEW: Use the email service's bulk reminder function
    result = KaratinaEmailService.send_bulk_reminders()
    sent = result['sent']
    skipped = result['skipped']

    if sent:
        messages.success(request,
            f'✅ {sent} reminder email(s) sent for tomorrow\'s appointments.')
    else:
        if skipped > 0:
            messages.info(request,
                f'No reminders sent. {skipped} patient(s) had no email address.')
        else:
            messages.info(request, 'No appointments scheduled for tomorrow.')

    return redirect('admin_dashboard')


# ── Management Command for Automated Reminders (Optional) ───────────────────
@staff_member_required
def send_scheduled_reminders(request):
    """
    Endpoint to trigger reminders - useful for scheduled tasks.
    This can be called by a cron job or Celery task.
    """
    from datetime import date, timedelta

    tomorrow = date.today() + timedelta(days=1)
    appointments = Appointment.objects.filter(
        slot__date=tomorrow,
        status__in=['pending', 'confirmed'],
    ).select_related('patient', 'slot')

    result = KaratinaEmailService.send_bulk_reminders()
    
    return redirect('admin_dashboard')