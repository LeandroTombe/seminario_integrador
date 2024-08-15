from django.urls import path
from .views import ResendOtpView ,ImportarAlumnoAPIView, UserPasswordResetUpdateView, UserRegisterView,UserLoginView,UserPasswordResetView,TestView, UserVerifyEmailView, LogoutAPIView


urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('importar_usuarios/', ImportarAlumnoAPIView.as_view(), name='importar_usuarios'),
    #path('importar_usuarios_panda/', ImportarAlumnoAPIView.as_view(), name='importar_usuarios'),
    path('reset/',UserPasswordResetView.as_view(),name='reset'),
    path('verify/',UserVerifyEmailView.as_view(),name='verify'),
    path('otpresend/',ResendOtpView.as_view(),name='otpresend'),
    path('resetpasswordupdate/',UserPasswordResetUpdateView.as_view(),name='password update'),
    path('api/logout/', LogoutAPIView.as_view(), name='logout'),
    
    path('test/', TestView.as_view(), name='test-view')

]