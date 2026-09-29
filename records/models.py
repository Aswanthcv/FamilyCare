from django.contrib.auth.models import User
from django.db import models


class FamilyMember(models.Model):
    SEX_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='family_members')
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text='Height in cm')
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text='Weight in kg')
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=150, blank=True)
    additional_notes = models.TextField(blank=True)

    def __str__(self):
        return self.full_name

    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
