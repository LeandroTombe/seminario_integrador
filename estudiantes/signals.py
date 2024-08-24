import logging
from django.db import IntegrityError
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Materia

# Configura el logger
logger = logging.getLogger('estudiantes')

@receiver(post_migrate)
def cargar_materias(sender, **kwargs):
    if sender.name == 'estudiantes':  # Asegúrate de que se ejecute solo para la app correcta
        logger.warning("Señal post_migrate ejecutada")

        from .models import Materia
        from .materias_iniciales import materias_iniciales

        for materia_data in materias_iniciales:
            if not Materia.objects.filter(nombre=materia_data['nombre']).exists():
                Materia.objects.create(**materia_data)
                logger.warning(f"Materia creada: {materia_data['nombre']}")
           