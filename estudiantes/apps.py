from django.apps import AppConfig
from django.db import IntegrityError


class EstudiantesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'estudiantes'
    
    def ready(self):
        import estudiantes.signals
