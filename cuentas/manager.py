from django.contrib.auth.models import BaseUserManager, Group
from django.core.exceptions import ValidationError
from django.core.validators import validate_email 
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    
    def create_user(self, legajo, nombre, apellido, password, documento,**extra_fields):
        if not legajo:
            raise ValueError(_("El legajo es requerido"))
        if not nombre:
            raise ValueError(_("El nombre es requerido"))
        if not apellido:
            raise ValueError(_("El apellido es requerido"))
        if not documento:
            raise ValueError(_("El documento es requerido"))
        
        user = self.model(legajo=legajo, nombre=nombre, apellido=apellido, documento=documento, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, legajo, nombre, apellido, password, documento, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("El campo 'is_staff' debe ser True para ser superusuario"))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("El campo 'is_superuser' debe ser True para ser superusuario"))

        user = self.create_user(legajo, nombre, apellido, password, documento, **extra_fields)
        
        # Asegúrate de que el usuario se ha guardado antes de asignar el grupo
        user.save(using=self._db)
        
        # Asignar el grupo "admin" al superusuario
        admin_group = Group.objects.get(name="Admin")
        user.groups.add(admin_group)
        
        # Guarda el usuario nuevamente para asegurarte de que la asignación del grupo se ha completado
        user.save(using=self._db)
        
        return user