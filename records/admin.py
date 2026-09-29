from django.contrib import admin
from .models import (
    FamilyMember,
    TestResult,
    MedicalReport,
    DoctorVisit,
    Prescription,
    Insurance,
    MedicalDocument,
)

admin.site.register([
    FamilyMember,
    TestResult,
    MedicalReport,
    DoctorVisit,
    Prescription,
    Insurance,
    MedicalDocument,
])


