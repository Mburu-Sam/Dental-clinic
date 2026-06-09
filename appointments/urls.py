from django.urls import path
from . import views

urlpatterns = [
    path('',                                    views.home,                    name='home'),
    path('services/',                           views.services_page,           name='services'),
    path('book/',                               views.book_appointment,        name='book_appointment'),
    path('mine/',                               views.my_appointments,         name='my_appointments'),
    path('cancel/<int:appointment_id>/',        views.cancel_appointment,      name='cancel_appointment'),
    path('dashboard/',                          views.admin_dashboard,         name='admin_dashboard'),
    path('confirm/<int:appointment_id>/',       views.confirm_appointment,     name='confirm_appointment'),
    path('admin-cancel/<int:appointment_id>/',  views.admin_cancel_appointment,name='admin_cancel_appointment'),
    path('contact/',                            views.contact,                 name='contact'),
    path('schedules/',                          views.manage_schedules,        name='manage_schedules'),
    path('send-reminders/',                     views.send_reminders_now,      name='send_reminders'),
]
