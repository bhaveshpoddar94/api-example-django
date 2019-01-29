from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

import views


urlpatterns = [
    url(r'^setup/$', views.SetupView.as_view(), name='setup'),
    url(r'^welcome/$', views.DoctorWelcome.as_view(), name='setup'),
    url(r'^kiosk/$', views.KioskView.as_view(), name='kiosk'),
    url(r'^fetch-appointments/(?P<id>[0-9]+)/$', 
        views.PatientAppointmentListView.as_view(), 
        name='fetch_appointments'),
    url(r'^update-information/(?P<p_id>[0-9]+)/(?P<a_id>[0-9]+)/$', 
        views.PatientInformationView.as_view(),
        name='update_information'),
    url(r'^begin-appointment/(?P<id>[0-9]+)/$', 
        views.begin_appointment,
        name='begin_appointment'),
    url(r'^complete-appointment/(?P<id>[0-9]+)/$', 
        views.complete_appointment,
        name='complete_appointment'),
    url(r'^analytics/$', views.analytics, name='analytics'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]