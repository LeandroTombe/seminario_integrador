from rest_framework.response import Response
from rest_framework import status,views,generics
from rest_framework.views import APIView
from .models import User
from tablib import Dataset
from .resources import UserResource
from django.http import HttpResponse
from .serializers import ResendOtpSerializer, UserPasswordResetUpdateserializer, UserRegisterSerializer,UserPasswordResetSerailizer,LogoutSerializer, UserVerifyEmailSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import Util
from django.contrib.auth.password_validation  import validate_password
from django.http import HttpResponsePermanentRedirect
import os
from .permissions import IsAlumno
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions  import ValidationError




class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']


class UserRegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Usuario creado exitosamente."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
  
    
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
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


class ImportarUsuariosAPIView(views.APIView):
    # permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        file = request.FILES['file']
        dataset = Dataset()
        imported_data = dataset.load(file.read().decode('utf-8'), format='csv')
        user_resource = UserResource()
        result = user_resource.import_data(dataset, dry_run=True)

        if not result.has_errors():
            user_resource.import_data(dataset, dry_run=False)
            return Response(status=status.HTTP_201_CREATED)
        else:
            # Serializar los errores a un formato JSON compatible
            error_messages = []
            for row in result.row_errors():
                for error in row[1]:
                    error_messages.append(str(error.error))

            return Response({"errors": error_messages}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({'msg':'Please check your email otp is send to password reset'},status=status.HTTP_200_OK)
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
                 return Response({"msg":"User does not exits"},status=status.HTTP_404_NOT_FOUND)
            try:
                 validate_password(password=password)
                 if password!=password2:
                            return Response({'msg':'Password and Confirm password did not match'},status=status.HTTP_404_NOT_FOUND)
            except ValidationError as err:
                 return Response(ValidationError({'password':err.messages})) 
            if user.otp!=otp:
                    return Response({'msg':'you have entered the wrong otp'},status=status.HTTP_404_NOT_FOUND)
            user.set_password(password)
            user.save()
            return Response({'msg':'password reset successfully'},status=status.HTTP_200_OK)
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
                    'msg': 'something went wrong',
                    'data': 'invalid email'
                }, status=status.HTTP_400_BAD_REQUEST)
            if user.otp != otp:
                return Response({
                    'msg': 'something went wrong',
                    'data': 'wrong otp'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.is_verified = True
            user.save()
            return Response({
                'msg': 'email verified'
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
                        return Response({'msg': 'OTP resent, please check your email.'}, status=status.HTTP_200_OK)
                else:
                        return Response({'msg': 'Email already verified'}, status=status.HTTP_200_OK)
            else:
                 return Response({'msg': 'User not found with the provided email'}, status=status.HTTP_404_NOT_FOUND) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    #permission_classes = (permissions.IsAuthenticated,)

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