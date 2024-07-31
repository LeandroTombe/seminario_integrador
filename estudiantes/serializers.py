from rest_framework import serializers


from .models import Materia,Cuota,Alumno,Cursado,CompromisoPago,Pago,Inhabilitation,Coordinador,Mensajes


class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = ('idMateria', 'nombre')

class CuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = ('nroCuota', 'año', 'importe', 'fechaVencimiento', 'importePagado')

class AlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumno
        fields = ('legajo', 'nombre', 'apellido', 'telefono', 'email', 'dni')

class CursadoSerializer(serializers.ModelSerializer):
    alumno = AlumnoSerializer()
    materia = MateriaSerializer()

    class Meta:
        model = Cursado
        fields = ('alumno', 'materia', 'año', 'cuatrimestre')

class CompromisoPagoSerializer(serializers.ModelSerializer):
    alumno = AlumnoSerializer()

    class Meta:
        model = CompromisoPago
        fields = ('alumno', 'periodo', 'fechaFirma')

class PagoSerializer(serializers.ModelSerializer):
    alumno = AlumnoSerializer()
    cuota = CuotaSerializer()

    class Meta:
        model = Pago
        fields = ('IDPago', 'alumno', 'cuota', 'montoInformado', 'fechaPagoInformado', 'montoConfirmado', 'fechaPagoConfirmado', 'comprobanteDePago', 'formaPago')

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