from django.shortcuts import render

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from cuentas.permissions import IsAlumno

from .models import Materia, Cuota, Alumno, Cursado, CompromisoPago, Pago, Inhabilitation, Coordinador, Mensajes
from .serializers import MateriaSerializer, CuotaSerializer, AlumnoSerializer, CursadoSerializer, CompromisoPagoSerializer, PagoSerializer, InhabilitationSerializer, CoordinadorSerializer, MensajesSerializer



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