from django.shortcuts import render

# Create your views here.
def notificaciones_vista(request):
    return render(request, 'notificaciones.html')