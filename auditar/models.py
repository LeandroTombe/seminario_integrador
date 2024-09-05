from django.utils import timezone
from django.db import models

class Auditoria(models.Model):
    CUATRIMESTRE_CHOICES = [
        (1, 'Primer Cuatrimestre'),
        (2, 'Segundo Cuatrimestre'),
    ]
    
    año = models.IntegerField(default=timezone.now().year)
    cuatrimestre = models.IntegerField(choices=CUATRIMESTRE_CHOICES)
    detalles = models.JSONField(default=dict, blank=True)
    fecha = models.DateTimeField(auto_now_add=True, editable=False)
    accion = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        # Truncar la fecha a la hora antes de guardar
        if not self.pk:  # Solo hacer esto cuando se crea el objeto
            now = timezone.now()
            self.fecha = now.replace(minute=0, second=0, microsecond=0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.año} - Cuatrimestre {self.cuatrimestre}"