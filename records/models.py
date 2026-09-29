from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


def validate_report_file(file):
    allowed_extensions = ('.pdf', '.jpg', '.jpeg', '.png')
    if not file.name.lower().endswith(allowed_extensions):
        raise ValidationError('Only PDF, JPG, JPEG, and PNG files are allowed.')


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


class TestResult(models.Model):
    family_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name='test_results')
    test_name = models.CharField(max_length=150)
    test_date = models.DateField()
    laboratory_or_hospital = models.CharField(max_length=150, blank=True)
    result_summary = models.TextField(blank=True)
    report_file = models.FileField(upload_to='test_reports/', blank=True, null=True, validators=[validate_report_file])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.test_name} - {self.family_member.full_name}'


class MedicalReport(models.Model):
    family_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name='medical_reports')
    report_title = models.CharField(max_length=150)
    report_date = models.DateField()
    hospital_or_clinic = models.CharField(max_length=150, blank=True)
    doctor_name = models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)
    report_file = models.FileField(upload_to='medical_reports/', blank=True, null=True, validators=[validate_report_file])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.report_title} - {self.family_member.full_name}'


class DoctorVisit(models.Model):
    family_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name='doctor_visits')
    doctor_name = models.CharField(max_length=150)
    hospital_or_clinic = models.CharField(max_length=150, blank=True)
    visit_date = models.DateField()
    reason_for_visit = models.TextField(blank=True)
    diagnosis_or_condition = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True)
    follow_up_date = models.DateField(blank=True, null=True)
    visit_document = models.FileField(upload_to='visit_documents/', blank=True, null=True, validators=[validate_report_file])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.doctor_name} - {self.family_member.full_name} ({self.visit_date})'


class Prescription(models.Model):
    family_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name='prescriptions')
    doctor_name = models.CharField(max_length=150)
    prescription_date = models.DateField()
    medicines = models.TextField()
    dosage_instructions = models.TextField(blank=True)
    duration = models.CharField(max_length=100, blank=True)
    prescription_file = models.FileField(upload_to='prescriptions/', blank=True, null=True, validators=[validate_report_file])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.doctor_name} - {self.family_member.full_name} ({self.prescription_date})'
