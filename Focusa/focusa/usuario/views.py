from django.shortcuts import render

def registrar(request):
    return render(request, 'registrar.html')

def iniciar_sesion(request):
    return render(request, 'login.html')
