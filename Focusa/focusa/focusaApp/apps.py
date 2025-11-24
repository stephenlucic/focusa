from django.apps import AppConfig


class FocusaappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'focusaApp'

    def ready(self):
        import focusaApp.signals  # Importar los signals al iniciar la aplicación