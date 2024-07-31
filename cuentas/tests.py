import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .factories import UserFactory

User = get_user_model()

#configurar el endpoint de la API

register= '/api/v1/auth/register/'
login= '/api/v1/auth/login/'


@pytest.mark.django_db
@pytest.mark.description("Pruebas para las vistas de registro y login de usuarios")
class TestUserRegisterView:
    def setup_method(self, method):
        self.client = APIClient()
        
    @pytest.mark.description("Prueba de registro de usuario exitoso")
    def test_user_registration_success(self):
        data = {
            'email': 'newuser@example.com',
            'nombre': 'John',
            'apellido': 'Doe',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        response = self.client.post(register, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'Usuario creado exitosamente.'
        assert User.objects.filter(email='newuser@example.com').exists()

    @pytest.mark.description("Prueba de registro de usuario con contraseñas no coincidentes")
    def test_user_registration_password_mismatch(self):
        data = {
            'email': 'newuser@example.com',
            'nombre': 'John',
            'apellido': 'Doe',
            'password': 'password123',
            'confirm_password': 'differentpassword'
        }
        response = self.client.post(register, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Las contraseñas no coinciden.' in response.data['non_field_errors']
        
    @pytest.mark.description("Prueba de registro de usuario con email duplicado")
    def test_user_registration_duplicate_email(self):
         # Crear un usuario primero
        User.objects.create_user(
            email='testuser3@example.com',
            nombre='Test',
            apellido='User',
            password='testpassword123'
        )
        # Intentar registrar otro usuario con el mismo correo
        data = {
            'email': 'testuser3@example.com',
            'nombre': 'Another',
            'apellido': 'User',
            'password': 'testpassword123',
            'confirm_password': 'testpassword123'
        }
        response = self.client.post(register, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    @pytest.mark.description("Prueba de registro de usuario con campos requeridos faltantes")
    def test_user_registration_missing_required_fields(self):
        data = {
            'email': '',
            'nombre': 'Test',
            'apellido': 'User',
            'password': '',
            'confirm_password': ''
        }
        response = self.client.post(register, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
        assert 'password' in response.data

    @pytest.mark.description("Prueba de registro de usuario con formato de email inválido")
    def test_user_registration_invalid_email_format(self):
        data = {
            'email': 'invalid-email-format',
            'nombre': 'Test',
            'apellido': 'User',
            'password': 'testpassword123',
            'confirm_password': 'testpassword123'
        }
        response = self.client.post(register, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

@pytest.mark.django_db
class TestUserLoginView:
    def setup_method(self, method):
        self.client = APIClient()
        self.user = UserFactory(email='user@example.com', password='password123')

    @pytest.mark.description("Prueba de login de usuario exitoso")
    def test_user_login_success(self):
        data = {
            'email': 'user@example.com',
            'password': 'password123'
        }
        response = self.client.post(login, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'refresh' in response.data
        assert 'access' in response.data

    @pytest.mark.description("Prueba de login de usuario con credenciales inválidas")
    def test_user_login_invalid_credentials(self):
        data = {
            'email': 'user@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(login, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['message'] == 'Contraseña incorrecta.'