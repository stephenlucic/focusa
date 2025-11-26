from django.shortcuts import render

# Create your views here.
def configuracion(request):
    return render(request, 'configuracion.html')