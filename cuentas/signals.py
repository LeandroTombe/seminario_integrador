from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    # Ejecutar solo para tu aplicación específica
    if sender.name == 'cuentas': 
        # Crear grupos necesarios
        group_names = ['Alumno', 'Coordinador', 'Admin']
        for name in group_names:
            Group.objects.get_or_create(name=name)