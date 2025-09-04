from django.apps import AppConfig


class AdminstratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'adminstrator'

    def ready(self):
        import adminstrator.signals
