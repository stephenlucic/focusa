# notificacion/context_processors.py
from .models import Notificacion

def notificaciones_header(request):
    if not request.user.is_authenticated:
        return {}

    qs = (
        Notificacion.objects
        .filter(usuario=request.user)
        .order_by('-creada_en')
    )

    return {
        "notif_no_leidas_count": qs.filter(leida=False).count(),
        "ultimas_notificaciones": qs[:4],
    }
