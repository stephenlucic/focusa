# notificacion/email_utils.py
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


def enviar_correo_notificacion(notificacion):
    usuario = notificacion.usuario

    # Si el usuario no tiene email, no hacemos nada
    if not usuario.email:
        return

    tarea = notificacion.tarea

    subject = f"[Focusa] {notificacion.titulo}"

    # URL de destino (ajusta los names a tus urls reales)
    try:
        if tarea:
            url_destino = settings.SITE_URL + reverse('kanban')
        else:
            url_destino = settings.SITE_URL + reverse('notificaciones')
    except Exception:
        # fallback por si algo falla
        url_destino = getattr(settings, "SITE_URL", "http://localhost:8000")

    saludo = usuario.first_name or usuario.username or "usuario"

    if tarea:
        estado = getattr(tarea, "estado", "N/A")
        prioridad = getattr(tarea, "prioridad", "N/A")
    else:
        estado = "N/A"
        prioridad = "N/A"

    message = (
        f"Hola {saludo},\n\n"
        f"{notificacion.mensaje}\n\n"
        f"Estado de la tarea: {estado}\n"
        f"Prioridad: {prioridad}\n\n"
        f"Puedes revisar esto en Focusa aquí:\n{url_destino}\n\n"
        "Saludos,\n"
        "Equipo Focusa"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [usuario.email],
        fail_silently=False,
    )
