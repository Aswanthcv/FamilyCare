from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FamilyMemberForm, RegistrationForm
from .models import FamilyMember


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
    return render(request, 'records/member_detail.html', {'member': member})


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
