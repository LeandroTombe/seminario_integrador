from rest_framework.response import Response
from rest_framework import status,views,generics
from rest_framework.views import APIView
from .models import User
from tablib import Dataset
from .resources import UserResource
from django.http import HttpResponse
from .serializers import ResendOtpSerializer, UserPasswordResetUpdateserializer, UserRegisterSerializer,UserPasswordResetSerailizer,LogoutSerializer, UserVerifyEmailSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import Util
from django.contrib.auth.password_validation  import validate_password
import os
from .permissions import IsAlumno
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions  import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from .serializers import CustomToken



#Registro de usuario

class UserRegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Usuario creado exitosamente."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

#Login de usuario
    
class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "Correo inexistente"}, status=status.HTTP_404_NOT_FOUND)
        if not user.check_password(password):
            return Response({"message": "Contraseña incorrecta."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generar un token JWT en lugar de usar Token
        refresh = CustomToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

class ImportarUsuariosAPIView(views.APIView):
    permission_classes = [IsAlumno]

    def post(self, request, *args, **kwargs):
        file = request.FILES['file']
        dataset = Dataset()
        imported_data = dataset.load(file.read().decode('utf-8'), format='csv')
        user_resource = UserResource()

        # Primera importación en modo "dry_run" para validar los datos
        result = user_resource.import_data(dataset, dry_run=True)

        valid_rows = []
        error_rows = []

        if result.has_errors():
            for row in result.row_errors():
                row_index = row[0] + 1
                for error in row[1]:
                    error_rows.append({
                        "row": row_index,
                        "error": str(error.error)
                    })

        if not result.has_errors():
            user_resource.import_data(dataset, dry_run=False)

            for row in dataset.dict:
                if all([row.get(col) for col in ['email', 'nombre', 'apellido']]):
                    valid_rows.append({
                        "legajo": row.get('legajo'),
                        "nombre": row.get('nombre'),
                        "apellido": row.get('apellido'),
                        "email": row.get('email')
                    })

            return Response({
                "message": "Usuarios importados correctamente",
                "valid_rows": valid_rows,
                "total_rows": len(valid_rows),
                "successful_imports": len(valid_rows),  # Asegúrate de incluir esto
                "failed_imports": 0  # Cambia esto si necesitas contabilizar los fallos
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "errors": error_rows,
                "total_rows": len(valid_rows),
                "failed_imports": len(error_rows),
                "successful_imports": len(valid_rows),  # También incluir esto en caso de error
                "valid_rows": valid_rows
            }, status=status.HTTP_400_BAD_REQUEST)
            
class ExportarUsuariosAPIView(views.APIView):
    #permission_classes = [CanExportData]

    def get(self, request, *args, **kwargs):
        user_resource = UserResource()
        dataset = user_resource.export()
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="usuarios.csv"'
        return response
    
#reseteo de password

class UserPasswordResetView(APIView):
    def post(self,request,fromat=None):
        serializer=UserPasswordResetSerailizer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email=serializer.validated_data['email']
            user=User.objects.filter(email=email).first()
            if user:
                Util.password_reset_otp(user.email)
                return Response({'msg':'Codigo para el reseteo de password enviado correctamente, por favor verifique su email'},status=status.HTTP_200_OK)
            return Response({'msg':'user is not exits'},status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.error,status=status.HTTP_400_BAD_REQUEST) 
    
    
class UserPasswordResetUpdateView(APIView):
    def post(self,request):
        serializer=UserPasswordResetUpdateserializer(data=request.data)
        print(serializer)
        if serializer.is_valid(raise_exception=True):
            password=serializer.validated_data['password']
            password2=serializer.validated_data['password2']
            otp=serializer.validated_data['otp']
            user=User.objects.filter(otp=otp).first()
            if not user:
                 return Response({"msg":"La cuenta no existe"},status=status.HTTP_404_NOT_FOUND)
            try:
                 validate_password(password=password)
                 if password!=password2:
                            return Response({'msg':'los password escritos no coinciden'},status=status.HTTP_404_NOT_FOUND)
            except ValidationError as err:
                 return Response(ValidationError({'password':err.messages})) 
            if user.otp!=otp:
                    return Response({'msg':'has ingresado un codigo incorrecto'},status=status.HTTP_404_NOT_FOUND)
            user.set_password(password)
            user.save()
            return Response({'msg':'el password se ha modificado correctamente'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class UserVerifyEmailView(APIView):
    def post(self, request):
        serializer = UserVerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            user = User.objects.filter(email=email).first()
            if not user:
                return Response({
                    'data': 'la cuenta con el email ingresado no existe'
                }, status=status.HTTP_400_BAD_REQUEST)
            if user.otp != otp:
                return Response({
                    'data': 'codigo incorrecto'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.is_verified = True
            user.save()
            return Response({
                'msg': 'email verificado correctamente'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendOtpView(APIView):
    def post(self, request):
        serializer = ResendOtpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if user :
                if not user.is_verified:   
                        Util.email_otp_verifcation(user.email)
                        return Response({'msg': 'codigo re enviado, por favor verifique en su email'}, status=status.HTTP_200_OK)
                else:
                        return Response({'msg': 'Email ya ha sidi verificado'}, status=status.HTTP_200_OK)
            else:
                 return Response({'msg': 'la cuenta con el email ingresado no existe'}, status=status.HTTP_404_NOT_FOUND) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


#testing para probar el permiso
class TestView(APIView):
    permission_classes = [IsAuthenticated, IsAlumno]

    def get(self, request, *args, **kwargs):
        return Response({"message": "Acceso concedido"}, status=status.HTTP_200_OK)
    


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer