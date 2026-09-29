from django.shortcuts import render


def home(request):
    """Display the initial dashboard placeholder."""
    return render(request, 'records/home.html')
