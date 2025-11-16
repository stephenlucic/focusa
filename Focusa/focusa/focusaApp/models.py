from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Perfil(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(max_length=20, blank=True)
    ocupacion = models.CharField(max_length=100, blank=True)
    genero = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ("M", "Masculino"),
            ("F", "Femenino"),
            ("O", "Otro"),
            ("N", "Prefiero no decir"),
        ],
    )
    pais = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.ocupacion or 'Sin ocupación'}"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.get_or_create(user=instance)
