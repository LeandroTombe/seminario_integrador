from django.urls import path
from .views import UserRegisterView,UserLoginView,ImportarUsuariosAPIView,PasswordTokenCheckAPI,SetNewPasswordAPIView,RequestPasswordResetEmail,TestView



urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('importar_usuarios/', ImportarUsuariosAPIView.as_view(), name='importar_usuarios'),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(),
         name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/',
         PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete', SetNewPasswordAPIView.as_view(),
         name='password-reset-complete'),
    path('test/', TestView.as_view(), name='test-view')

]