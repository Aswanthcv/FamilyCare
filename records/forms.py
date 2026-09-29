from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import DoctorVisit, FamilyMember, Insurance, MedicalDocument, MedicalReport, Prescription, TestResult


class NoFutureDateFormMixin:
    """Reject dates after today for records describing past health events."""

    past_date_fields = ()

    def clean(self):
        cleaned_data = super().clean()
        for field_name in self.past_date_fields:
            selected_date = cleaned_data.get(field_name)
            if selected_date and selected_date > date.today():
                self.add_error(field_name, 'This date cannot be in the future.')
        return cleaned_data


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Family Name'
        self.fields['username'].help_text = 'Enter the family name used to log in.'
        self.fields['password1'].help_text = 'Use at least 8 characters.'
        self.fields['password2'].help_text = ''

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class FamilyMemberForm(NoFutureDateFormMixin, forms.ModelForm):
    past_date_fields = ('date_of_birth',)

    class Meta:
        model = FamilyMember
        exclude = ('user',)
        widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date'})}


class TestResultForm(NoFutureDateFormMixin, forms.ModelForm):
    past_date_fields = ('test_date',)

    class Meta:
        model = TestResult
        exclude = ('family_member', 'created_at')
        widgets = {'test_date': forms.DateInput(attrs={'type': 'date'})}


class MedicalReportForm(NoFutureDateFormMixin, forms.ModelForm):
    past_date_fields = ('report_date',)

    class Meta:
        model = MedicalReport
        exclude = ('family_member', 'created_at')
        widgets = {'report_date': forms.DateInput(attrs={'type': 'date'})}


class DoctorVisitForm(NoFutureDateFormMixin, forms.ModelForm):
    past_date_fields = ('visit_date',)

    class Meta:
        model = DoctorVisit
        exclude = ('family_member', 'created_at')
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date'}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date'}),
        }


class PrescriptionForm(NoFutureDateFormMixin, forms.ModelForm):
    past_date_fields = ('prescription_date',)

    class Meta:
        model = Prescription
        exclude = ('family_member', 'created_at')
        widgets = {'prescription_date': forms.DateInput(attrs={'type': 'date'})}


class InsuranceForm(forms.ModelForm):
    class Meta:
        model = Insurance
        exclude = ('family_member', 'created_at')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }


class MedicalDocumentForm(NoFutureDateFormMixin, forms.ModelForm):
    past_date_fields = ('document_date',)

    class Meta:
        model = MedicalDocument
        exclude = ('family_member', 'created_at')
        widgets = {'document_date': forms.DateInput(attrs={'type': 'date'})}
