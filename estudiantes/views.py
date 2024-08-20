from django.shortcuts import render

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from cuentas.permissions import IsAlumno
from rest_framework import status

from .models import Materia, Cuota, Alumno, Cursado, ParametrosCompromiso, CompromisoPago, Pago, Inhabilitation, Coordinador, Mensajes
from .serializers import MateriaSerializer, CuotaSerializer, AlumnoSerializer, CursadoSerializer, ParametrosCompromisoSerializer, CompromisoPagoSerializer, PagoSerializer, InhabilitationSerializer, CoordinadorSerializer, MensajesSerializer
from datetime import datetime


class MateriasView(APIView):
    permission_classes = [IsAuthenticated, IsAlumno]

    def get(self, request, *args, **kwargs):
        # Lógica para listar materias
        return Response({"message": "Acceso permitido a materias para Alumno"}, status=200)

#Crud de materia


#creacion de materia
class MateriaCreateView(generics.CreateAPIView):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer
    permission_classes = [IsAuthenticated, IsAlumno]

#listado de materias

class MateriaListView(generics.ListAPIView):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer
    permission_classes = [IsAuthenticated, IsAlumno]

#actualizacion de materia
class MateriaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer
    permission_classes = [IsAuthenticated, IsAlumno]
    
#crud de pagos

class PagoListCreateView(generics.ListCreateAPIView):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    
    
class PagoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    
class AllPagoListView(generics.ListAPIView):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    
class PagoUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer
    partial = True
    
    
class PagoDeleteView(generics.DestroyAPIView):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(print("Pago eliminado"))

class ParametrosCompromisoSetValores(APIView):
    #permission_classes = [IsAuthenticated, IsAlumno]    #Cambiar rol
    
    def post(self, request, *args, **kwargs):

        serializer=ParametrosCompromisoSerializer(data=request.data)

        if serializer.is_valid():
            parametros = serializer.save()
            return Response({"message": "Compromiso de pago dado de alta"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompromisoActualView(APIView):

    def get(self, request, *args, **kwargs):
        queryset = ParametrosCompromiso.objects.filter(año=datetime.now().year)    # Buscar forma de filtrar el compromiso actual
        serializer = ParametrosCompromisoSerializer(queryset, many=True)

        if queryset:
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class AllCompromisoListView(APIView):
    
    def get(self, request, *args, **kwargs):
        queryset = ParametrosCompromiso.objects.all()
        serializer = ParametrosCompromisoSerializer(queryset, many=True)
        
        if queryset:
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class ParametrosCompromisoEditar(APIView):
    def put(self, request, *args, **kwargs):
        año = request.data.get('año')  # Obtener el año desde los datos de la solicitud

        if not año:
            return Response({"error": "El año es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            compromiso = ParametrosCompromiso.objects.get(año=año)  # Encuentra el compromiso existente
        except ParametrosCompromiso.DoesNotExist:
            return Response({"error": "Compromiso de pago no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ParametrosCompromisoSerializer(compromiso, data=request.data, partial=True)  # Usar partial=True para permitir actualizaciones parciales

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Compromiso de pago actualizado exitosamente"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)