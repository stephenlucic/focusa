# suscripcion/models.py :contentReference[oaicite:1]{index=1}
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()


class Plan(models.Model):
    class Periodo(models.TextChoices):
        MENSUAL = "monthly", "Mensual"
        ANUAL = "yearly", "Anual"

    codigo = models.SlugField(
        unique=True,
        help_text="Identificador interno: basic, pro, etc."
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio_clp = models.PositiveIntegerField(default=0)
    periodo = models.CharField(
        max_length=20,
        choices=Periodo.choices,
        default=Periodo.MENSUAL,
    )
    dias_prueba = models.PositiveIntegerField(default=0)
    es_activo = models.BooleanField(default=True)
    es_destacado = models.BooleanField(default=False)

    max_tareas = models.PositiveIntegerField(null=True, blank=True)
    max_tags = models.PositiveIntegerField(null=True, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["precio_clp"]  # opcional: siempre te saldrán ordenados por precio

    def __str__(self):
        return f"{self.nombre} ({self.precio_clp} CLP/{self.periodo})"


class MetodoPago(models.Model):
    codigo = models.SlugField(
        unique=True,
        help_text="Ej: webpay, transferencia, tarjeta_mock"
    )
    nombre = models.CharField(max_length=100)
    es_activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Suscripcion(models.Model):
    class Estado(models.TextChoices):
        ACTIVA = "active", "Activa"
        CANCELADA = "canceled", "Cancelada"
        EXPIRADA = "expired", "Expirada"
        PRUEBA = "trialing", "En período de prueba"
        PENDIENTE = "pending", "Pendiente de pago"
        MOROSA = "past_due", "Pago atrasado"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="suscripciones",
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name="suscripciones",
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PRUEBA,
    )
    # 👇 mejora: te ahorras tener que pasar siempre fecha_inicio a mano
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    auto_renovar = models.BooleanField(default=True)

    proveedor_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="ID de suscripción en el proveedor externo (ficticio por ahora).",
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Suscripción de {self.usuario} a {self.plan.nombre}"

    @property
    def esta_activa(self) -> bool:
        now = timezone.now()
        if self.estado not in [self.Estado.ACTIVA, self.Estado.PRUEBA]:
            return False
        if self.fecha_fin and self.fecha_fin < now:
            return False
        return True


class Pago(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pending", "Pendiente"
        COMPLETADO = "completed", "Completado"
        FALLIDO = "failed", "Fallido"
        REEMBOLSADO = "refunded", "Reembolsado"

    suscripcion = models.ForeignKey(
        Suscripcion,
        on_delete=models.CASCADE,
        related_name="pagos",
    )
    metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.PROTECT,
        related_name="pagos",
    )
    monto_clp = models.PositiveIntegerField()
    moneda = models.CharField(max_length=10, default="CLP")
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    fecha_pago = models.DateTimeField(null=True, blank=True)

    referencia_proveedor = models.CharField(
        max_length=255,
        blank=True,
        help_text="ID/orden que devolvería el proveedor de pago (mock).",
    )
    mensaje_error = models.TextField(blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago {self.monto_clp} CLP - {self.estado}"

@receiver(post_save, sender=User)
def crear_trial_pro_al_crear_usuario(sender, instance, created, **kwargs):
    """
    Cuando se crea un usuario, si existe el plan PRO,
    se le asigna una suscripción en prueba por 'dias_prueba' días.
    """
    if not created:
        return

    # Si por alguna razón ya tiene suscripciones, no duplicar
    if Suscripcion.objects.filter(usuario=instance).exists():
        return

    plan_pro = Plan.objects.filter(codigo="pro", es_activo=True).first()
    if not plan_pro:
        return  # si no existe el plan, salimos piola

    now = timezone.now()
    dias = plan_pro.dias_prueba or 7
    fecha_fin = now + timedelta(days=dias)

    Suscripcion.objects.create(
        usuario=instance,
        plan=plan_pro,
        estado=Suscripcion.Estado.PRUEBA,
        fecha_inicio=now,
        fecha_fin=fecha_fin,
        auto_renovar=False,
    )