from django.db import models
from .validators import validar_nombre
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from datetime import datetime

class Materia(models.Model):
    codigo_materia = models.IntegerField(primary_key=True ,auto_created=True)
    nombre = models.CharField(max_length=50, validators=[validar_nombre])

    def __str__(self):
        return self.nombre

class Alumno(models.Model):
    legajo = models.IntegerField()
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.IntegerField( null=True, blank=True)
    dni = models.IntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    pago_al_dia = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    materias = models.ManyToManyField(Materia, related_name='alumnos')

    def __str__(self):
        return f'{self.nombre} {self.apellido} {self.dni}'

class Cuota(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('informada', 'Informada'),
        ('vencida', 'Vencida')
    ]
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    nroCuota = models.IntegerField()
    año = models.IntegerField()
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    moraPrimerVencimiento = models.DecimalField(max_digits=10, decimal_places=2)
    fechaPrimerVencimiento = models.DateField()
    moraSegundoVencimiento = models.DecimalField(max_digits=10, decimal_places=2)
    fechaSegundoVencimiento = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    importePagado = models.DecimalField(max_digits=10, decimal_places=2)
    importeInformado = models.DecimalField(max_digits=10, decimal_places=2)
    fechaImporteInformado = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES,default='Pendiente')
    pagos = models.ManyToManyField('Pago', through='DetallePago')

    def aplicar_moras(self, compromiso):
        hoy = datetime.now().date()

        if self.estado == "Pagada":
            return

        if self.alumno.materias.count() > 2:
            completo = True
        else:
            completo = False

        if hoy > self.fechaSegundoVencimiento:
            if self.estado == 'Pendiente':
                self.estado = 'Vencida'
            if completo:
                self.moraPrimerVencimiento = compromiso.importe_pri_venc_comp
                self.moraSegundoVencimiento = compromiso.importe_seg_venc_comp
            else:
                self.moraPrimerVencimiento = compromiso.importe_pri_venc_red
                self.moraSegundoVencimiento = compromiso.importe_seg_venc_red

            if self.total < (self.importe + self.moraPrimerVencimiento + self.moraSegundoVencimiento):
                self.total += self.moraPrimerVencimiento + self.moraSegundoVencimiento

        elif hoy > self.fechaPrimerVencimiento:
            if self.estado == 'Pendiente':
                self.estado = 'Vencida'
            if completo:
                self.moraPrimerVencimiento = compromiso.importe_pri_venc_comp
            else:
                self.moraPrimerVencimiento = compromiso.importe_pri_venc_red
            
            if self.total != (self.importe + self.moraPrimerVencimiento):
                self.total += self.moraPrimerVencimiento

        # Guardar los cambios después de aplicar las moras
        self.save()

    def __str__(self):
        return f'Cuota {self.nroCuota} - Año {self.año}'


class Cursado(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    #agregar o verificar la comision
    año = models.IntegerField()
    cuatrimestre = models.IntegerField()

    def __str__(self):
        return f'{self.alumno} - {self.materia}'

class ParametrosCompromiso(models.Model):
    año = models.IntegerField()
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
            return f'Año: {self.año} - Cuatrimestre: {self.cuatrimestre}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['año', 'cuatrimestre'], name='unique_año_cuatrimestre')
        ]
    
from django.db import models

class FirmaCompromiso(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    parametros_compromiso = models.ForeignKey(ParametrosCompromiso, on_delete=models.CASCADE)
    fechaFirma = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('alumno', 'parametros_compromiso')

    def __str__(self):
        return f'{self.alumno} - {self.parametros_compromiso.año} - {self.parametros_compromiso.cuatrimestre} - {self.fechaFirma}'


class Pago(models.Model):
    TRANSFERENCIA = 'Transferencia'
    EFECTIVO = 'Efectivo'
    FORMA_PAGO_CHOICES = [
        (TRANSFERENCIA, 'Transferencia'),
        (EFECTIVO, 'Efectivo'),
    ]

    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='pagos')
    numero_recibo = models.IntegerField()
    monto_confirmado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_pago_confirmado = models.DateField(null=True, blank=True)
    comprobante_de_pago = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    forma_pago = models.CharField(max_length=20, choices=FORMA_PAGO_CHOICES, default=TRANSFERENCIA)
    cuotas = models.ManyToManyField('Cuota', through='DetallePago')


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
    


class Notificacion(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='notificaciones')
    tipo_evento = models.CharField(max_length=100)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    visto = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.alumno} - {self.tipo_evento}"
    
    
class DetallePago(models.Model):
    pago = models.ForeignKey('Pago', on_delete=models.CASCADE)
    cuota = models.ForeignKey('Cuota', on_delete=models.CASCADE)
    monto_cuota = models.DecimalField(max_digits=10, decimal_places=2)
    

    def __str__(self):
        return f'Pago {self.pago.id} - Cuota {self.cuota.nroCuota}'

    class Meta:
        unique_together = ('pago', 'cuota')

class SolicitudProrroga(models.Model):
    PENDIENTE = 'Pendiente'
    APROBADA = 'Aprobada'
    RECHAZADA = 'Rechazada'
    
    ESTADO_CHOICES = [
        (PENDIENTE, 'Pendiente'),
        (APROBADA, 'Aprobada'),
        (RECHAZADA, 'Rechazada'),
    ]
    
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    analitico = models.FileField(upload_to='prorroga/')
    motivo = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=PENDIENTE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    comentarios = models.TextField(null=True, blank=True)
    fecha_evaluacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Solicitud de {self.alumno} para {self.materia} - {self.estado}'

class SolicitudBajaProvisoria(models.Model):
    PENDIENTE = 'Pendiente'
    APROBADA = 'Aprobada'
    RECHAZADA = 'Rechazada'
    
    ESTADO_CHOICES = [
        (PENDIENTE, 'Pendiente'),
        (APROBADA, 'Aprobada'),
        (RECHAZADA, 'Rechazada'),
    ]
    
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    compromiso = models.ForeignKey(ParametrosCompromiso, on_delete=models.CASCADE)
    motivo = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=PENDIENTE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    comentarios = models.TextField(null=True, blank=True)
    fecha_evaluacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Solicitud de {self.alumno} para {self.compromiso} - {self.estado}'