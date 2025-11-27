# configuracion/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from suscripcion.models import Suscripcion  # 👈 importar

@login_required
def configuracion(request):
    suscripcion_actual = (
        Suscripcion.objects
        .filter(usuario=request.user)
        .order_by("-fecha_inicio")
        .first()
    )

    context = {
        "suscripcion_actual": suscripcion_actual,
    }
    return render(request, "configuracion.html", context)
