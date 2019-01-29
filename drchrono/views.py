from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView
from django.http import JsonResponse
from django.db.models import Avg
from social_django.models import UserSocialAuth

from drchrono.forms import CheckinForm, PatientInformationForm
from drchrono.endpoints import (
    DoctorEndpoint, 
    PatientSummaryEndpoint,
    PatientEndpoint,
    AppointmentEndpoint)
from drchrono.models import WaitTime

import datetime as dt
import random

def get_token():
    """
    Social Auth module is configured to store our access tokens. This dark 
    magic will fetch it for us if we've already signed in.
    """
    oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
    access_token = oauth_provider.extra_data['access_token']
    return access_token

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


class SetupView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, 
    and saves the token.
    """
    template_name = 'kiosk_setup.html'


class DoctorWelcome(TemplateView):
    """
    The doctor's dashboard after successfully logging into their account.
    """
    template_name = 'doctor_welcome.html'

    def get_context_data(self, **kwargs):
        kwargs = super(DoctorWelcome, self).get_context_data(**kwargs)
        access_token = get_token()
        dt_api = DoctorEndpoint(access_token)
        ap_api = AppointmentEndpoint(access_token)
        pt_api = PatientSummaryEndpoint(access_token)
        doctor = next(dt_api.list())
        appointments = list(ap_api.list(date=dt.date.today()))
        app_list = []
        for a in appointments:
            patient_info = pt_api.fetch(id=a["patient"])
            a["patient_info"] = patient_info
            a['start_time'] = dt.datetime.strptime(
                a["scheduled_time"], "%Y-%m-%dT%H:%M:%S")
            a['end_time'] = a["start_time"]\
                + dt.timedelta(minutes=int(a["duration"]))
            updated_at =  dt.datetime.strptime(
                a['updated_at'], "%Y-%m-%dT%H:%M:%S")
            wait_time = dt.datetime.now() - updated_at
            a["wait_time"] = round(wait_time.total_seconds() / 60)
            app_list.append(a)
        confirmed = filter(lambda x: x["status"] == "", app_list)
        current = filter(lambda x: x["status"] == "In Session", app_list)
        arrived = filter(lambda x: x["status"] == "Arrived", app_list)
        complete = filter(lambda x: x["status"] == "Complete", app_list)
        kwargs['doctor'] = doctor
        kwargs['confirmed'] = confirmed
        kwargs['current'] = current
        kwargs['arrived'] = arrived
        kwargs['complete'] = complete
        return kwargs

@method_decorator(login_required, name='dispatch')
class KioskView(FormView):
    """
    Form for the incoming patients to check in at the kiosk.
    """
    template_name = 'patient_check_in.html'
    form_class = CheckinForm
    success_url = '/update-information/'

    def form_valid(self, form):
        first_name = form.cleaned_data['first_name']
        last_name  = form.cleaned_data['last_name']
        params = {'first_name': first_name, 'last_name': last_name}
        access_token = get_token()
        api = PatientSummaryEndpoint(access_token)
        patient = list(api.list(params=params))
        if patient:
            p = patient[0]
            return redirect('fetch_appointments', p['id'])
        form.add_error(None, "No patient found matching this name!")
        return super(KioskView, self).form_invalid(form)


class PatientAppointmentListView(TemplateView):
    """
    Patient's webpage to view appointments upo check-in at the kiosk.
    """
    template_name = 'patient_appointment.html'

    def get_context_data(self, **kwargs):
        kwargs = super(PatientAppointmentListView, self).get_context_data(**kwargs)
        patient_id = self.kwargs['id']
        access_token = get_token()
        ap_api = AppointmentEndpoint(access_token)
        pt_api = PatientSummaryEndpoint(access_token)
        ap_params = {"patient": patient_id}
        patient_info = pt_api.fetch(id=patient_id)
        appointments = list(ap_api.list(params=ap_params, date=dt.date.today()))
        for a in appointments:
            a['start_time'] = dt.datetime.strptime(
                a["scheduled_time"], "%Y-%m-%dT%H:%M:%S")
            a['end_time'] = a["start_time"]\
                + dt.timedelta(minutes=int(a["duration"]))
        kwargs["patient_info"] = patient_info
        kwargs["appointments"] = appointments
        return kwargs
        

@method_decorator(login_required, name='dispatch')
class PatientInformationView(FormView):
    """
    Form to update patient information after they check in at the kiosk.
    """
    template_name = 'patient_information.html'
    form_class = PatientInformationForm
    success_url = '/kiosk/'
    
    def form_valid(self, form):
        patient_id = self.kwargs['p_id']
        appointment_id = self.kwargs['a_id']
        access_token = get_token()
        api = PatientEndpoint(access_token)
        ap_api = AppointmentEndpoint(access_token)
        data = form.cleaned_data
        api.update(id=patient_id, data=data)
        ap_api.update(id=appointment_id, data={"status": "Arrived"})
        return super(PatientInformationView, self).form_valid(form)

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super(PatientInformationView, self).get_initial()
        patient_id = self.kwargs['p_id']
        access_token = get_token()
        api = PatientEndpoint(access_token)
        patient_info = api.fetch(id=patient_id)
        initial = merge_two_dicts(patient_info, initial)
        return initial

def begin_appointment(request, id):
    access_token = get_token()
    api = AppointmentEndpoint(access_token)
    appointment = api.fetch(id=id)
    updated_at =  dt.datetime.strptime(
        appointment['updated_at'], "%Y-%m-%dT%H:%M:%S")
    wait_time = dt.datetime.now() - updated_at
    diff = round(wait_time.total_seconds() / 60)
    wt = WaitTime(appointment_id=id, wait_time=diff)
    wt.save()
    api.update(id=id, data={"status": "In Session"})
    return redirect('/welcome')

def complete_appointment(request, id):
    access_token = get_token()
    api = AppointmentEndpoint(access_token)
    api.update(id=id, data={"status": "Complete"})
    return redirect('/welcome')

def analytics(request):
    wtimes = WaitTime.objects.all()
    avg_wt = wtimes.aggregate(Avg('wait_time'))
    context = {"average_wait_time": avg_wt['wait_time__avg']}
    return render(request, 'analytics.html', context=context)

