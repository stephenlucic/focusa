from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from suscripcion.models import Suscripcion
import os


def avatar_upload_path(instance, filename):
    """
    Ruta dinámica: archivos/perfiles/<user_id>_<slug_username>/<timestamp>_<origname>
    Ej: perfiles/3_blablax20/20251124_143502_avatar.jpg
    """
    name, ext = os.path.splitext(filename)
    slug = slugify(instance.user.username or f"user{instance.user.id}")
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{timestamp}_{slug}{ext.lower()}"
    return os.path.join("perfiles", f"{instance.user.id}_{slug}", new_filename)

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
    avatar = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.ocupacion or 'Sin ocupación'}"

    @property
    def suscripcion_activa(self):
        now = timezone.now()
        return (
            Suscripcion.objects
            .filter(
                usuario=self.user,
                estado__in=[Suscripcion.Estado.ACTIVA, Suscripcion.Estado.PRUEBA],
            )
            .filter(
                models.Q(fecha_fin__isnull=True) |
                models.Q(fecha_fin__gte=now)
            )
            .order_by("-fecha_inicio")
            .first()
        )

    @property
    def plan_actual(self):
        sub = self.suscripcion_activa
        return sub.plan if sub else None

# crear perfil al crear user
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.get_or_create(user=instance)

# eliminar archivo anterior al actualizar avatar
@receiver(pre_save, sender=Perfil)
def eliminar_avatar_antiguo(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Perfil.objects.get(pk=instance.pk)
    except Perfil.DoesNotExist:
        return
    old_file = old.avatar
    new_file = instance.avatar
    if old_file and old_file != new_file:
        if os.path.isfile(old_file.path):
            try:
                os.remove(old_file.path)
            except Exception:
                pass

# eliminar archivo al borrar el objeto
@receiver(post_delete, sender=Perfil)
def borrar_avatar_al_eliminar(sender, instance, **kwargs):
    avatar = instance.avatar
    if avatar and os.path.isfile(avatar.path):
        try:
            os.remove(avatar.path)
        except Exception:
            pass
