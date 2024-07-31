from django.db import models
from .validators import validar_nombre

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
    legajo = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    telefono = models.IntegerField()
    email = models.EmailField()
    dni = models.IntegerField()

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

class Cursado(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    año = models.IntegerField()
    cuatrimestre = models.IntegerField()

    def __str__(self):
        return f'{self.alumno} - {self.materia}'

class CompromisoPago(models.Model):
    alumno = models.OneToOneField(Alumno, on_delete=models.CASCADE)
    periodo = models.CharField(max_length=255)
    fechaFirma = models.DateField()

    def __str__(self):
        return f'{self.alumno} - {self.periodo}'

class Pago(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    cuota = models.ForeignKey(Cuota, on_delete=models.CASCADE)
    IDPago = models.IntegerField(primary_key=True)
    montoInformado = models.FloatField()
    fechaPagoInformado = models.DateField()
    montoConfirmado = models.FloatField()
    fechaPagoConfirmado = models.DateField()
    comprobanteDePago = models.CharField(max_length=255)
    formaPago = models.CharField(max_length=255)

    def __str__(self):
        return f'Pago {self.IDPago} - {self.alumno}'

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