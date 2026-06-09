from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/',     admin.site.urls),
    path('accounts/',  include('accounts.urls')),
    path('',           include('appointments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ── Customise admin branding ─────────────────────────────────────────────────
admin.site.site_header  = "Karatina Dental Clinic — Admin"
admin.site.site_title   = "Karatina Dental Admin"
admin.site.index_title  = "Clinic Management Panel"
