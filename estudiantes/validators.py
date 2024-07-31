from django.core.exceptions import ValidationError


def validar_nombre(value):
    if not value.isalpha():
        raise ValidationError(
            '%(value)s debe contener solo letras',
            params={'value': value},
        )