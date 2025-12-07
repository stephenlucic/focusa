from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.contrib.auth import get_user_model

from .models import Notificacion
from Kanban.models import Tarea 
from .email_utils import enviar_correo_notificacion 
import logging

User = get_user_model()
logger = logging.getLogger(__name__)



def _obtener_destinatario(tarea: Tarea):
    """
    Decide a quién le llega la notificación.
    Puedes ajustar esta lógica a tu modelo real:
    - tarea.responsable
    - tarea.creador
    - etc.
    """
    # Prueba primero con responsable, si existe:
    if hasattr(tarea, 'responsable') and tarea.responsable:
        return tarea.responsable

    # Luego intenta con creador/autor:
    if hasattr(tarea, 'creador') and tarea.creador:
        return tarea.creador

    return None


@receiver(post_save, sender=Tarea)
def crear_notificacion_creacion_actualizacion(sender, instance, created, **kwargs):
    destinatario = _obtener_destinatario(instance)
    if not destinatario:
        return

    if created:
        accion = 'creacion'
        titulo = f"Nueva tarea: {instance.titulo}"
        mensaje = (
            f"Se creó la tarea «{instance.titulo}» "
            f"con estado {getattr(instance, 'estado', 'N/A')} "
            f"y prioridad {getattr(instance, 'prioridad', 'N/A')}."
        )
    else:
        accion = 'actualizacion'
        titulo = f"Tarea actualizada: {instance.titulo}"
        mensaje = f"La tarea «{instance.titulo}» fue actualizada."

    Notificacion.objects.create(
        usuario=destinatario,
        tarea=instance,
        accion=accion,
        titulo=titulo,
        mensaje=mensaje,
    )


@receiver(post_delete, sender=Tarea)
def crear_notificacion_eliminacion(sender, instance, **kwargs):
    destinatario = _obtener_destinatario(instance)
    if not destinatario:
        return

    Notificacion.objects.create(
        usuario=destinatario,
        tarea=None,  # la tarea ya se eliminó, por eso permitimos null en el modelo
        accion='eliminacion',
        titulo=f"Tarea eliminada: {instance.titulo}",
        mensaje=f"La tarea «{instance.titulo}» fue eliminada.",
    )

@receiver(post_save, sender=Notificacion)
def enviar_correo_cuando_se_crea_notificacion(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        enviar_correo_notificacion(instance)
    except Exception as e:
        # Si falla el envío de email, solo loguear pero no interrumpir
        logger.warning(f"Error al enviar correo de notificación: {e}")