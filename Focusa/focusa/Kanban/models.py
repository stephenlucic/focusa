from django.db import models
from django.conf import settings

class Tag(models.Model):
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

    def __str__(self):
        return f"{self.titulo} ({self.get_estado_display()})"
