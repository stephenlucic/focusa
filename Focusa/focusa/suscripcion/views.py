# suscripcion/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import Plan, Suscripcion, MetodoPago, Pago


@login_required
def suscripcion(request):
    # Planes activos
    planes = Plan.objects.filter(es_activo=True).order_by("precio_clp")
    # Métodos de pago activos
    metodos_pago = MetodoPago.objects.filter(es_activo=True)

    # Si no hay métodos de pago, creamos uno de prueba
    if not metodos_pago.exists():
        MetodoPago.objects.get_or_create(
            codigo="mock",
            defaults={"nombre": "Pago de prueba", "es_activo": True},
        )
        metodos_pago = MetodoPago.objects.filter(es_activo=True)

    # Suscripción actual (última)
    suscripcion_actual = (
        Suscripcion.objects
        .filter(usuario=request.user)
        .order_by("-fecha_inicio")
        .first()
    )

    if request.method == "POST":
        plan_codigo = request.POST.get("plan_codigo")
        metodo_codigo = request.POST.get("metodo_pago")

        if not plan_codigo or not metodo_codigo:
            messages.error(request, "Debes seleccionar un plan y un método de pago.")
            return redirect("suscripcion")  # name definido en urls.py :contentReference[oaicite:2]{index=2}

        plan = get_object_or_404(Plan, codigo=plan_codigo, es_activo=True)
        metodo = get_object_or_404(MetodoPago, codigo=metodo_codigo, es_activo=True)

        # 1) Cerrar suscripción anterior (si existe)
        if suscripcion_actual:
            suscripcion_actual.estado = Suscripcion.Estado.CANCELADA
            suscripcion_actual.fecha_fin = timezone.now()
            suscripcion_actual.save()

        # 2) Crear nueva suscripción
        now = timezone.now()
        fecha_fin = now + timedelta(days=30)  # por ahora todos los planes duran 1 mes

        nueva_sub = Suscripcion.objects.create(
            usuario=request.user,
            plan=plan,
            estado=Suscripcion.Estado.ACTIVA if plan.precio_clp > 0 else Suscripcion.Estado.ACTIVA,
            fecha_inicio=now,
            fecha_fin=fecha_fin,
            auto_renovar=True if plan.precio_clp > 0 else False,
        )

        # 3) Crear pago ficticio sólo si el plan es pagado
        if plan.precio_clp > 0:
            Pago.objects.create(
                suscripcion=nueva_sub,
                metodo_pago=metodo,
                monto_clp=plan.precio_clp,
                estado=Pago.Estado.COMPLETADO,
                fecha_pago=now,
                referencia_proveedor="PAGO-DEMO-123",
            )

        messages.success(request, f"Tu plan ha sido cambiado a {plan.nombre}.")
        # puedes redirigir a configuración si quieres:
        # return redirect("configuracion:configuracion")
        return redirect("configuracion")

    context = {
        "planes": planes,
        "metodos_pago": metodos_pago,
        "suscripcion_actual": suscripcion_actual,
    }
    return render(request, "suscripcion.html", context)
