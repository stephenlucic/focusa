from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache  
from django.http import JsonResponse

from .models import Notificacion


# @login_required
@never_cache
def notificaciones_vista(request):
    if request.method == 'POST':
        # Marcar todas las notificaciones del usuario como leídas
        Notificacion.objects.filter(
            usuario=request.user,
            leida=False
        ).update(leida=True)

        return redirect('notificaciones')

    notificaciones = Notificacion.objects.filter(
        usuario=request.user
    ).order_by('-creada_en')

    return render(request, 'notificaciones.html', {
        'notificaciones': notificaciones,
    })

def notificaciones_count(request):
    """
    Devuelve cuántas notificaciones no leídas tiene el usuario.
    """
    count = Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).count()
    return JsonResponse({'count': count})