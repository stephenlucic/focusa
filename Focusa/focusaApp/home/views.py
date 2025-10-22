from django.shortcuts import render
from django.http import HttpResponse, Http404

def home_inicio(request):
    # return HttpResponse("¡Bienvenido a la página de inicio de Focusa!")
    return render(request, 'home/home.html', {})

