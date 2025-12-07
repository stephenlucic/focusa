from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache  
from django.http import JsonResponse
from django.views.decorators.http import require_POST


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

@require_POST
@login_required
def eliminar_notificacion(request, pk):
    """Elimina una notificación específica del usuario"""
    notificacion = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    notificacion.delete()
    return JsonResponse({'ok': True})

@require_POST
@login_required
def eliminar_todas_notificaciones(request):
    """Elimina todas las notificaciones del usuario"""
    Notificacion.objects.filter(usuario=request.user).delete()
    return JsonResponse({'ok': True})