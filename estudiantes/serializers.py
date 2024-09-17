from rest_framework import serializers


from .models import Notificacion,Materia,Cuota,Alumno,Cursado,ParametrosCompromiso,FirmaCompromiso,Pago,Inhabilitation,Coordinador,Mensajes


class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = ('codigo_materia', 'nombre')

class CuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = ('nroCuota', 'año', 'importe', 'moraPrimerVencimiento', 'fechaPrimerVencimiento', 'moraSegundoVencimiento', 'fechaSegundoVencimiento', 'total', 'importePagado')

class AlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumno
        fields = '__all__'

class CursadoSerializer(serializers.ModelSerializer):
    alumno = AlumnoSerializer()
    materia = MateriaSerializer()

    class Meta:
        model = Cursado
        fields = ('alumno', 'materia', 'año', 'cuatrimestre')

class ParametrosCompromisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParametrosCompromiso
        fields = ('año', 'cuatrimestre', 'compromiso_contenido', 'importe_matricula', 'importe_reducido', 'importe_completo', 'importe_pri_venc_comp', 'importe_pri_venc_red', 'importe_seg_venc_comp', 'importe_seg_venc_red')

class FirmaCompromisoSerializer(serializers.ModelSerializer):
    alumno = AlumnoSerializer()

    class Meta:
        model = FirmaCompromiso
        fields = ('alumno', 'parametros_compromiso' ,'fechaFirma')
        read_only_fields = ['fecha_firma']


class PagoSerializer(serializers.ModelSerializer):
    alumno = AlumnoSerializer()
    class Meta:
        model = Pago
        fields = ('id','alumno', 'monto_informado', 'fecha_pago_informado', 'monto_confirmado', 'fecha_pago_confirmado', 'comprobante_de_pago', 'forma_pago')
        
        
class InhabilitationSerializer(serializers.ModelSerializer):
    alumno = AlumnoSerializer()

    class Meta:
        model = Inhabilitation
        fields = ('alumno', 'fechaInicio', 'fechaFin', 'motivo', 'tipo')

class CoordinadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinador
        fields = ('codCoor', 'nombre', 'apellido', 'telefono', 'email', 'dni')

class MensajesSerializer(serializers.ModelSerializer):
    alumno = AlumnoSerializer()

    class Meta:
        model = Mensajes
        fields = ('alumno', 'periodo', 'fechaFirma')
        
class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = ['id', 'alumno', 'mensaje', 'fecha']