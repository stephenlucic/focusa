from django.db import models
from django.conf import settings

class Notificacion(models.Model):
    ACCION_CHOICES = [
        ('creacion', 'Creación'),
        ('actualizacion', 'Actualización'),
        ('eliminacion', 'Eliminación'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    # importante: permitir null porque la tarea se puede eliminar
    tarea = models.ForeignKey(
        'Kanban.Tarea',        # ajusta 'kanban' por el nombre real de tu app de tareas
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notificaciones'
    )

    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField(blank=True)

    leida = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creada_en']

    def __str__(self):
        return f"{self.get_accion_display()} - {self.titulo}"

