from rest_framework import serializers
from .models import Auditoria

class AuditoriaSerializer(serializers.ModelSerializer):
    fecha = serializers.DateTimeField(format="%d/%m/%Y %H:%M")

    class Meta:
        model = Auditoria
        fields = '__all__'