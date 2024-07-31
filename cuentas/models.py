from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .manager import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email= models.EmailField(max_length=255, unique=True, verbose_name=_("Direccion email"))
    nombre= models.CharField(max_length=100, verbose_name=_("nombre"))
    apellido= models.CharField(max_length=100, verbose_name=_("apellido"))
    is_staff= models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified= models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined= models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD= "email"
    
    
    REQUIRED_FIELDS = ["nombre", "apellido"]
    
    
    objects= UserManager()
    
    def __str__(self):
        return self.email
    
    @property
    def get_full_name(self):
        return f"{self.nombre} { self.apellido}"
    
    def tokens(self):
        pass
    
    
