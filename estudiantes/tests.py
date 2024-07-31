import pytest
from django.db.utils import IntegrityError
from .models import Materia

from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch


@pytest.mark.django_db
def test_create_materia():
    # Crear una instancia de Materia
    materia = Materia.objects.create(
        idMateria=1,
        nombre='Matemáticas'
    )
    
    # Verificar que la instancia se haya guardado correctamente
    assert Materia.objects.count() == 1
    assert materia.nombre == 'Matemáticas'
    assert str(materia) == 'Matemáticas'

@pytest.mark.django_db
def test_create_materia_duplicate_id():
    # Crear una instancia de Materia
    Materia.objects.create(
        idMateria=1,
        nombre='Matemáticas'
    )
    
    # Intentar crear otra Materia con el mismo idMateria
    with pytest.raises(IntegrityError):
        Materia.objects.create(
            idMateria=1,
            nombre='Ciencias'
        )

@pytest.mark.django_db
def test_update_materia():
    # Crear una instancia de Materia
    materia = Materia.objects.create(
        idMateria=1,
        nombre='Matemáticas'
    )
    
    # Actualizar la instancia
    materia.nombre = 'Matemáticas Avanzadas'
    materia.save()
    
    # Verificar que los cambios se hayan guardado
    updated_materia = Materia.objects.get(idMateria=1)
    assert updated_materia.nombre == 'Matemáticas Avanzadas'

@pytest.mark.django_db
def test_delete_materia():
    # Crear una instancia de Materia
    materia = Materia.objects.create(
        idMateria=1,
        nombre='Matemáticas'
    )
    
    # Eliminar la instancia
    materia.delete()
    
    # Verificar que la instancia haya sido eliminada
    assert Materia.objects.count() == 0

@pytest.mark.django_db
def test_materia_string_representation():
    # Crear una instancia de Materia
    materia = Materia.objects.create(
        idMateria=1,
        nombre='Matemáticas'
    )
    
    # Verificar la representación en cadena
    assert str(materia) == 'Matemáticas'
    