from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import FamilyMember


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
