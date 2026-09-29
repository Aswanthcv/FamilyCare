from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DoctorVisitForm, FamilyMemberForm, InsuranceForm, MedicalDocumentForm, MedicalReportForm, PrescriptionForm, RegistrationForm, TestResultForm
from .models import DoctorVisit, FamilyMember, Insurance, MedicalDocument, MedicalReport, Prescription, TestResult


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('records:home')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            return redirect('records:home')
        return render(request, 'registration/login.html', {'error': 'The username or password is incorrect.'})
    return render(request, 'registration/login.html')


def user_logout(request):
    logout(request)
    return redirect('records:login')


@login_required
def home(request):
    members = FamilyMember.objects.filter(user=request.user)
    return render(request, 'records/home.html', {'members': members})


@login_required
def add_member(request):
    if request.method == 'POST':
        form = FamilyMemberForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save(commit=False)
            member.user = request.user
            member.save()
            return redirect('records:home')
    else:
        form = FamilyMemberForm()
    return render(request, 'records/member_form.html', {'form': form, 'title': 'Add Family Member'})


@login_required
def member_detail(request, member_id):
    member = get_object_or_404(FamilyMember, id=member_id, user=request.user)
    return render(request, 'records/member_detail.html', {
        'member': member,
        'test_results': member.test_results.all(),
        'medical_reports': member.medical_reports.all(),
        'doctor_visits': member.doctor_visits.all(),
        'prescriptions': member.prescriptions.all(),
        'insurance_records': member.insurance_records.all(),
        'medical_documents': member.medical_documents.all(),
    })


@login_required
def add_test_result(request, member_id):
    member = get_object_or_404(FamilyMember, id=member_id, user=request.user)
    if request.method == 'POST':
        form = TestResultForm(request.POST, request.FILES)
        if form.is_valid():
            test_result = form.save(commit=False)
            test_result.family_member = member
            test_result.save()
            return redirect('records:member_detail', member_id=member.id)
    else:
        form = TestResultForm()
    return render(request, 'records/test_result_form.html', {'form': form, 'member': member, 'title': 'Add Test Result'})


@login_required
def edit_test_result(request, test_result_id):
    test_result = get_object_or_404(TestResult, id=test_result_id, family_member__user=request.user)
    if request.method == 'POST':
        form = TestResultForm(request.POST, request.FILES, instance=test_result)
        if form.is_valid():
            form.save()
            return redirect('records:member_detail', member_id=test_result.family_member.id)
    else:
        form = TestResultForm(instance=test_result)
    return render(request, 'records/test_result_form.html', {'form': form, 'member': test_result.family_member, 'title': 'Edit Test Result'})


@login_required
def delete_test_result(request, test_result_id):
    test_result = get_object_or_404(TestResult, id=test_result_id, family_member__user=request.user)
    if request.method == 'POST':
        member_id = test_result.family_member.id
        test_result.delete()
        return redirect('records:member_detail', member_id=member_id)
    return render(request, 'records/test_result_confirm_delete.html', {'test_result': test_result})


@login_required
def view_test_report(request, test_result_id):
    test_result = get_object_or_404(TestResult, id=test_result_id, family_member__user=request.user)
    if not test_result.report_file:
        return redirect('records:member_detail', member_id=test_result.family_member.id)
    return FileResponse(test_result.report_file.open('rb'), as_attachment=False, filename=test_result.report_file.name)


@login_required
def add_medical_report(request, member_id):
    member = get_object_or_404(FamilyMember, id=member_id, user=request.user)
    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.family_member = member
            report.save()
            return redirect('records:member_detail', member_id=member.id)
    else:
        form = MedicalReportForm()
    return render(request, 'records/medical_report_form.html', {'form': form, 'member': member, 'title': 'Add Medical Report'})


@login_required
def edit_medical_report(request, report_id):
    report = get_object_or_404(MedicalReport, id=report_id, family_member__user=request.user)
    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            form.save()
            return redirect('records:member_detail', member_id=report.family_member.id)
    else:
        form = MedicalReportForm(instance=report)
    return render(request, 'records/medical_report_form.html', {'form': form, 'member': report.family_member, 'title': 'Edit Medical Report'})


@login_required
def delete_medical_report(request, report_id):
    report = get_object_or_404(MedicalReport, id=report_id, family_member__user=request.user)
    if request.method == 'POST':
        member_id = report.family_member.id
        report.delete()
        return redirect('records:member_detail', member_id=member_id)
    return render(request, 'records/medical_report_confirm_delete.html', {'report': report})


@login_required
def view_medical_report(request, report_id):
    report = get_object_or_404(MedicalReport, id=report_id, family_member__user=request.user)
    if not report.report_file:
        return redirect('records:member_detail', member_id=report.family_member.id)
    return FileResponse(report.report_file.open('rb'), as_attachment=False, filename=report.report_file.name)


@login_required
def add_doctor_visit(request, member_id):
    member = get_object_or_404(FamilyMember, id=member_id, user=request.user)
    if request.method == 'POST':
        form = DoctorVisitForm(request.POST, request.FILES)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.family_member = member
            visit.save()
            return redirect('records:member_detail', member_id=member.id)
    else:
        form = DoctorVisitForm()
    return render(request, 'records/doctor_visit_form.html', {'form': form, 'member': member, 'title': 'Add Doctor Visit'})


@login_required
def edit_doctor_visit(request, visit_id):
    visit = get_object_or_404(DoctorVisit, id=visit_id, family_member__user=request.user)
    if request.method == 'POST':
        form = DoctorVisitForm(request.POST, request.FILES, instance=visit)
        if form.is_valid():
            form.save()
            return redirect('records:member_detail', member_id=visit.family_member.id)
    else:
        form = DoctorVisitForm(instance=visit)
    return render(request, 'records/doctor_visit_form.html', {'form': form, 'member': visit.family_member, 'title': 'Edit Doctor Visit'})


@login_required
def doctor_visit_detail(request, visit_id):
    visit = get_object_or_404(DoctorVisit, id=visit_id, family_member__user=request.user)
    return render(request, 'records/doctor_visit_detail.html', {'visit': visit})


@login_required
def delete_doctor_visit(request, visit_id):
    visit = get_object_or_404(DoctorVisit, id=visit_id, family_member__user=request.user)
    if request.method == 'POST':
        member_id = visit.family_member.id
        visit.delete()
        return redirect('records:member_detail', member_id=member_id)
    return render(request, 'records/doctor_visit_confirm_delete.html', {'visit': visit})


@login_required
def view_visit_document(request, visit_id):
    visit = get_object_or_404(DoctorVisit, id=visit_id, family_member__user=request.user)
    if not visit.visit_document:
        return redirect('records:member_detail', member_id=visit.family_member.id)
    return FileResponse(visit.visit_document.open('rb'), as_attachment=False, filename=visit.visit_document.name)


@login_required
def add_prescription(request, member_id):
    member = get_object_or_404(FamilyMember, id=member_id, user=request.user)
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.family_member = member
            prescription.save()
            return redirect('records:member_detail', member_id=member.id)
    else:
        form = PrescriptionForm()
    return render(request, 'records/prescription_form.html', {'form': form, 'member': member, 'title': 'Add Prescription'})


@login_required
def prescription_detail(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id, family_member__user=request.user)
    return render(request, 'records/prescription_detail.html', {'prescription': prescription})


@login_required
def edit_prescription(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id, family_member__user=request.user)
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, request.FILES, instance=prescription)
        if form.is_valid():
            form.save()
            return redirect('records:member_detail', member_id=prescription.family_member.id)
    else:
        form = PrescriptionForm(instance=prescription)
    return render(request, 'records/prescription_form.html', {'form': form, 'member': prescription.family_member, 'title': 'Edit Prescription'})


@login_required
def delete_prescription(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id, family_member__user=request.user)
    if request.method == 'POST':
        member_id = prescription.family_member.id
        prescription.delete()
        return redirect('records:member_detail', member_id=member_id)
    return render(request, 'records/prescription_confirm_delete.html', {'prescription': prescription})


@login_required
def view_prescription_file(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id, family_member__user=request.user)
    if not prescription.prescription_file:
        return redirect('records:member_detail', member_id=prescription.family_member.id)
    return FileResponse(prescription.prescription_file.open('rb'), as_attachment=False, filename=prescription.prescription_file.name)


@login_required
def add_insurance(request, member_id):
    member = get_object_or_404(FamilyMember, id=member_id, user=request.user)
    if request.method == 'POST':
        form = InsuranceForm(request.POST, request.FILES)
        if form.is_valid():
            insurance = form.save(commit=False)
            insurance.family_member = member
            insurance.save()
            return redirect('records:member_detail', member_id=member.id)
    else:
        form = InsuranceForm()
    return render(request, 'records/insurance_form.html', {'form': form, 'member': member, 'title': 'Add Insurance'})


@login_required
def insurance_detail(request, insurance_id):
    insurance = get_object_or_404(Insurance, id=insurance_id, family_member__user=request.user)
    return render(request, 'records/insurance_detail.html', {'insurance': insurance})


@login_required
def edit_insurance(request, insurance_id):
    insurance = get_object_or_404(Insurance, id=insurance_id, family_member__user=request.user)
    if request.method == 'POST':
        form = InsuranceForm(request.POST, request.FILES, instance=insurance)
        if form.is_valid():
            form.save()
            return redirect('records:member_detail', member_id=insurance.family_member.id)
    else:
        form = InsuranceForm(instance=insurance)
    return render(request, 'records/insurance_form.html', {'form': form, 'member': insurance.family_member, 'title': 'Edit Insurance'})


@login_required
def delete_insurance(request, insurance_id):
    insurance = get_object_or_404(Insurance, id=insurance_id, family_member__user=request.user)
    if request.method == 'POST':
        member_id = insurance.family_member.id
        insurance.delete()
        return redirect('records:member_detail', member_id=member_id)
    return render(request, 'records/insurance_confirm_delete.html', {'insurance': insurance})


@login_required
def view_insurance_card(request, insurance_id):
    insurance = get_object_or_404(Insurance, id=insurance_id, family_member__user=request.user)
    if not insurance.insurance_card:
        return redirect('records:member_detail', member_id=insurance.family_member.id)
    return FileResponse(insurance.insurance_card.open('rb'), as_attachment=False, filename=insurance.insurance_card.name)


@login_required
def add_medical_document(request, member_id):
    member = get_object_or_404(FamilyMember, id=member_id, user=request.user)
    if request.method == 'POST':
        form = MedicalDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.family_member = member
            document.save()
            return redirect('records:member_detail', member_id=member.id)
    else:
        form = MedicalDocumentForm()
    return render(request, 'records/medical_document_form.html', {'form': form, 'member': member, 'title': 'Upload Medical Document'})


@login_required
def medical_document_detail(request, document_id):
    document = get_object_or_404(MedicalDocument, id=document_id, family_member__user=request.user)
    return render(request, 'records/medical_document_detail.html', {'document': document})


@login_required
def edit_medical_document(request, document_id):
    document = get_object_or_404(MedicalDocument, id=document_id, family_member__user=request.user)
    if request.method == 'POST':
        form = MedicalDocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            return redirect('records:member_detail', member_id=document.family_member.id)
    else:
        form = MedicalDocumentForm(instance=document)
    return render(request, 'records/medical_document_form.html', {'form': form, 'member': document.family_member, 'title': 'Edit Medical Document'})


@login_required
def delete_medical_document(request, document_id):
    document = get_object_or_404(MedicalDocument, id=document_id, family_member__user=request.user)
    if request.method == 'POST':
        member_id = document.family_member.id
        document.delete()
        return redirect('records:member_detail', member_id=member_id)
    return render(request, 'records/medical_document_confirm_delete.html', {'document': document})


@login_required
def view_medical_document(request, document_id):
    document = get_object_or_404(MedicalDocument, id=document_id, family_member__user=request.user)
    return FileResponse(document.document_file.open('rb'), as_attachment=False, filename=document.document_file.name)


@login_required
def edit_member(request, member_id):
    member = get_object_or_404(FamilyMember, id=member_id, user=request.user)
    if request.method == 'POST':
        form = FamilyMemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            return redirect('records:member_detail', member_id=member.id)
    else:
        form = FamilyMemberForm(instance=member)
    return render(request, 'records/member_form.html', {'form': form, 'title': 'Edit Family Member', 'member': member})


@login_required
def delete_member(request, member_id):
    member = get_object_or_404(FamilyMember, id=member_id, user=request.user)
    if request.method == 'POST':
        member.delete()
        return redirect('records:home')
    return render(request, 'records/member_confirm_delete.html', {'member': member})
