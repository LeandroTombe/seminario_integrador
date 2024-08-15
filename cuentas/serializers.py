from rest_framework import serializers
from .models import User
from django.contrib.auth import get_user_model

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'nombre', 'apellido', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    

    
#Reseteo de password

class UserPasswordResetSerailizer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=100)
    class Meta:
        model=User
        fields=['email']

class UserPasswordResetUpdateserializer(serializers.Serializer):
      password=serializers.CharField(max_length=50,style={'input_type':'password'},write_only=True)
      password2=serializers.CharField(max_length=50,style={'input_type':'password'},write_only=True)
      otp=serializers.CharField()
     
      class Meta:
        model=User
        fields=['otp','password','password2']
        
class UserVerifyEmailSerializer(serializers.Serializer):
    email=serializers.CharField()
    otp=serializers.CharField()
    
       
class  ResendOtpSerializer(serializers.Serializer):
    email=serializers.CharField()
     

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            refresh_token = RefreshToken(self.token)
            refresh_token.blacklist()
        except Exception as e:
            self.fail('bad_token')


#agregar el email al token


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, User):
        print("desde custom:",User.groups)
        token = super().get_token(User)
        token['role'] = User.groups.first().name if User.groups.exists() else 'no_role'
        return token
    
class CustomToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        print("desde refresh:", user)
        token = super().for_user(user)
        # Agregar el rol del usuario al token
        token['role'] = user.groups.first().name if user.groups.exists() else 'no_role'
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer