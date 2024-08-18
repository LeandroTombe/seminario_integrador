from rest_framework_simplejwt.tokens import AccessToken

class CustomAccessToken(AccessToken):
    @property
    def role(self):
        user = self.user
        print(user.groups.all())
        if user.groups.filter(name='alumno').exists():
            return 'alumno'
        # Agrega otros roles aquí si es necesario
        return 'holis'