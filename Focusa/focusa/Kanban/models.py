from django.db import models
from django.conf import settings
import os
from django.utils import timezone
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

def tarea_attachment_upload_path(instance, filename):
    """archivos/adjuntos/user_<user_id>/<YYYYMMDD_HHMMSS>_<slug>.<ext>"""
    name, ext = os.path.splitext(filename)
    slug_name = slugify(instance.responsable.username or f"user{instance.responsable.id}")
    slug = slugify(instance.titulo[:30] or f"task{instance.responsable_id}")
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    ext = ext.lower()
    return os.path.join("adjuntos", f"{instance.responsable_id}_{slug_name}", f"{timestamp}_{slug}{ext}")

class Tag(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="kanban_tags",
        null=True,
        blank=True,  # para no romper los tags viejos globales
    )
    nombre = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#0d6efd")  # formato #RRGGBB

    def __str__(self):
        return self.nombre


class Tarea(models.Model):
    PRIORIDAD_CHOICES = [
        ("alta", "Alta"),
        ("media", "Media"),
        ("baja", "Baja"),
    ]

    ESTADO_CHOICES = [
        ("todo", "Por hacer"),
        ("progress", "En progreso"),
        ("review", "En revisión"),
        ("done", "Completado"),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default="media")
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="todo")
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tareas"
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tareas"
    )
    fecha_desde = models.DateField(null=True, blank=True)
    fecha_hasta = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to=tarea_attachment_upload_path, null=True, blank=True)

    def __str__(self):
        return f"{self.titulo} ({self.get_estado_display()})"

# borrar fichero cuando se elimina la tarea
@receiver(post_delete, sender=Tarea)
def borrar_attachment_al_eliminar(sender, instance, **kwargs):
    if instance.attachment:
        try:
            if os.path.isfile(instance.attachment.path):
                os.remove(instance.attachment.path)
        except Exception:
            pass

# eliminar fichero anterior al actualizar attachment
@receiver(pre_save, sender=Tarea)
def eliminar_attachment_antiguo(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Tarea.objects.get(pk=instance.pk)
    except Tarea.DoesNotExist:
        return
    old_file = old.attachment
    new_file = instance.attachment
    if old_file and old_file != new_file:
        try:
            if old_file.path and os.path.isfile(old_file.path):
                os.remove(old_file.path)
        except Exception:
            pass
