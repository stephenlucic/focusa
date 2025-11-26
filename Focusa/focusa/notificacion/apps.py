from django.apps import AppConfig


class NotificacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notificacion'

    def ready(self):
        import notificacion.signals  # Importa los signals al iniciar la aplicación