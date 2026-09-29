from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import FamilyMember, MedicalReport, TestResult


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class FamilyMemberForm(forms.ModelForm):
    class Meta:
        model = FamilyMember
        exclude = ('user',)
        widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date'})}


class TestResultForm(forms.ModelForm):
    class Meta:
        model = TestResult
        exclude = ('family_member', 'created_at')
        widgets = {'test_date': forms.DateInput(attrs={'type': 'date'})}


class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        exclude = ('family_member', 'created_at')
        widgets = {'report_date': forms.DateInput(attrs={'type': 'date'})}
