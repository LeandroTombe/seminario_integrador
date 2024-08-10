#validaciones asociadas a la importacion de datos

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User=get_user_model()

def validate_csv_file(file):
    # Validación del formato del archivo
    if not file.name.endswith('.csv'):
        raise ValidationError("El archivo debe ser un CSV.")
    
    # Validación de tamaño del archivo
    max_size_mb = 100
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"El archivo no puede exceder {max_size_mb} MB.")
    
    return True

def validate_row_data(row, required_columns,row_number):
    """
    Validar los datos de una fila específica del archivo CSV.
    """
    email = row.get('email')
    nombre = row.get('nombre')
    apellido = row.get('apellido')
    row_number = row_number + 1  # Incrementar el número de fila en 1 para que comience desde 1
    
    if not any(row.values()):
        return (False, None)

    if email and User.objects.filter(email=email).exists():
        raise ValueError(f"Error en la fila {row_number}: El usuario con el email {email} ya existe. La fila será ignorada.")
    
    if all(not row.get(field) for field in required_columns):
        return (False, None)  # Ignorar la fila si todos los campos esenciales están vacíos
    
    
    print(row)
    return (True, row) 
    
   
   
    

def validate_duplicates(dataset, model_class):
    # Validación de duplicados (por ejemplo, email único)
    emails = [row['email'] for row in dataset.dict]
    existing_emails = model_class.objects.filter(email__in=emails).values_list('email', flat=True)
    
    if existing_emails:
        raise ValidationError(f"Los siguientes correos ya existen: {', '.join(existing_emails)}")
    
    return True