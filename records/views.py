from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RegistrationForm


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
    return render(request, 'records/home.html')
