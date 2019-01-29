from django import forms
from django.forms import widgets


# Add your forms here
class CheckinForm(forms.Form):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField()



GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
)

RACE_CHOICES = (
    ('blank', "Blank"), 
    ('indian', "Indian"), 
    ('asian', "Asian"), 
    ('black', "Black"), 
    ('hawaiian', "Hawaiian"), 
    ('white', "White"),
    ('declined', "Decline")
)

ETHNICITY_CHOICES = (
    ('blank', "Blank"), 
    ('hispanic', "Hispanic"), 
    ('not_hispanic', "Not Hispanic"),
    ('declined', "Decline")
)

class PatientInformationForm(forms.Form):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField()
    social_security_number = forms.CharField(required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    email = forms.EmailField(required=False)
    cell_phone = forms.CharField(required=False)
    ethnicity = forms.ChoiceField(choices=ETHNICITY_CHOICES)
    race = forms.ChoiceField(choices=RACE_CHOICES)

    