from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FamilyMemberForm, MedicalReportForm, RegistrationForm, TestResultForm
from .models import FamilyMember, MedicalReport, TestResult


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
