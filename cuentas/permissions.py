from rest_framework.permissions import BasePermission

class IsAlumno(BasePermission):
    def has_permission(self, request, view):
        # Verificar si el usuario está autenticado
        print(request.user.groups.all())
        if not request.user or not request.user.is_authenticated:
            return False

        # Verificar si el usuario pertenece a los grupos requeridos
        return request.user.groups.filter(name='Alumno').exists()
