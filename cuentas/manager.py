from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email 
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("Por favor, ingrese un email valido "))
        
    def create_user(self, email, nombre, apellido, password, **extra_fields):
        if email:
            email=self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_("El email es requerido "))
        if not nombre:
            raise ValueError(_("El nombre es requerido"))
        if not apellido:
            raise ValueError(_("El apellido es requerido"))
        user=self.model(email=email,nombre=nombre, apellido=apellido,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    
    def create_superuser(self, email, nombre, apellido, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("el staff debe ser verdadero para ser superusuario"))
        
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("la opcion de superusuario tiene que ser verdadero"))
        
        user=self.create_user(email, nombre, apellido, password, **extra_fields)
        user.save(using=self._db)
        return user