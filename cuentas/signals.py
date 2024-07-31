from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    # Ejecutar solo para tu aplicación específica
    if sender.name == 'cuentas':  # Cambia 'myapp' por el nombre de tu aplicación
        Group.objects.get_or_create(name='Alumno')