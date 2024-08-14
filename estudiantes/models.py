from django.db import models
from .validators import validar_nombre
from django.conf import settings

class Materia(models.Model):
    idMateria = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=50, validators=[validar_nombre])

    def __str__(self):
        return self.nombre

class Cuota(models.Model):
    nroCuota = models.IntegerField()
    año = models.IntegerField()
    importe = models.FloatField()
    fechaVencimiento = models.DateField()
    importePagado = models.FloatField()

    def __str__(self):
        return f'Cuota {self.nroCuota} - Año {self.año}'

class Alumno(models.Model):
    legajo = models.IntegerField()
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.IntegerField( null=True, blank=True)
    dni = models.IntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    def __str__(self):
        return f'{self.nombre} {self.apellido}'


class Cursado(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    año = models.IntegerField()
    cuatrimestre = models.IntegerField()

    def __str__(self):
        return f'{self.alumno} - {self.materia}'

class ParametrosCompromiso(models.Model):
    año = models.IntegerField(primary_key=True)
    cuatrimestre = models.IntegerField()
    compromiso_contenido = models.FileField(upload_to='compromiso/', null=True, blank=True)
    importe_matricula = models.DecimalField(max_digits=10, decimal_places=2)
    importe_reducido = models.DecimalField(max_digits=10, decimal_places=2)
    importe_completo = models.DecimalField(max_digits=10, decimal_places=2)
    importe_pri_venc_comp = models.DecimalField(max_digits=10, decimal_places=2)
    importe_pri_venc_red = models.DecimalField(max_digits=10, decimal_places=2)
    importe_seg_venc_comp = models.DecimalField(max_digits=10, decimal_places=2)
    importe_seg_venc_red = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.año} - {self.cuatrimestre}'

    #class Meta:
    #    constraints = [
    #        models.UniqueConstraint(
    #            fields=['año', 'cuatrimestre'], name='unique_año_cuatrimestre_combination'
    #        )
    #    ]

class CompromisoPago(models.Model):
    alumno = models.OneToOneField(Alumno, on_delete=models.CASCADE, null=True)  #Modificar relacion
    parametros_compromiso = models.ForeignKey(ParametrosCompromiso, on_delete=models.CASCADE, null=True)
    fechaFirma = models.DateField()

    def __str__(self):
        return f'{self.alumno} - {self.parametros_compromiso.año} - {self.parametros_compromiso.cuatrimestre}'

from django.db import models


class Pago(models.Model):
    TRANSFERENCIA = 'Transferencia'
    EFECTIVO = 'Efectivo'
    FORMA_PAGO_CHOICES = [
        (TRANSFERENCIA, 'Transferencia'),
        (EFECTIVO, 'Efectivo'),
    ]

    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='pagos')
    monto_informado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago_informado = models.DateField()
    monto_confirmado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_pago_confirmado = models.DateField(null=True, blank=True)
    comprobante_de_pago = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    forma_pago = models.CharField(max_length=20, choices=FORMA_PAGO_CHOICES, default=TRANSFERENCIA)

    def __str__(self):
        return f'Pago {self.pk} - {self.alumno.nombre} {self.alumno.apellido}'
    
    
class Inhabilitation(models.Model):
    alumno = models.OneToOneField(Alumno, on_delete=models.CASCADE)
    fechaInicio = models.DateField()
    fechaFin = models.DateField()
    motivo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.alumno} - {self.motivo}'

class Coordinador(models.Model):
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    telefono = models.IntegerField()
    email = models.EmailField()
    dni = models.IntegerField()
    codCoor = models.IntegerField(primary_key=True)

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

class Mensajes(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    periodo = models.CharField(max_length=255)
    fechaFirma = models.DateField()

    def __str__(self):
        return f'{self.alumno} - {self.periodo}'