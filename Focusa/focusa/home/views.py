from django.shortcuts import render, redirect
from django.conf import settings

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)  # p.ej. /focusa/dashboard/
    return render(request, 'home.html')