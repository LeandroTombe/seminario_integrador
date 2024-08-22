from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group
from django.utils.translation import gettext_lazy as _
from .manager import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    legajo= models.CharField(max_length=255, unique=True, verbose_name=_("legajo"))
    apellido= models.CharField(max_length=100, verbose_name=_("apellido"))
    nombre= models.CharField(max_length=100, verbose_name=_("nombre"))
    otp=models.CharField(max_length=6,null=True)
    is_staff= models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified= models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined= models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    group = models.CharField(max_length=50, choices=[('alumno', 'Alumno'), ('coordinador', 'Coordinador'), ('admin', 'Admin')]) 
    
    USERNAME_FIELD= "legajo"
    
    
    REQUIRED_FIELDS = ["nombre", "apellido"]
    
    
    objects= UserManager()
    
    def __str__(self):
        return self.legajo
    
    @property
    def get_full_name(self):
        return f"{self.nombre} { self.apellido}"
    
    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        