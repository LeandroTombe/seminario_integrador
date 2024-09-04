from .models import Cuota
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.db.models import F, Q

def alta_cuotas(alumno, compromiso):

    # Obtener la cantidad de materias que el alumno está cursando
    cantidad_materias = alumno.materias.count()

    # Determinar el importe según la cantidad de materias
    if cantidad_materias > 2:
        importe = compromiso.importe_completo
    else:
        importe = compromiso.importe_reducido

    # Determinar los números de cuotas según el cuatrimestre
    if compromiso.cuatrimestre == 1:
        cuotas = range(3, 8)  # Cuotas 3, 4, 5, 6, 7
    else:
        cuotas = range(8, 13)  # Cuotas 8, 9, 10, 11, 12

    for nro_cuota in cuotas:
        # Calcular las fechas de vencimiento como el día 10 y el día 20 del mes de la cuota
        mes_vencimiento = nro_cuota
        año_vencimiento = compromiso.año

        fecha_primer_vencimiento = datetime(año_vencimiento, mes_vencimiento, 10)
        fecha_segundo_vencimiento = datetime(año_vencimiento, mes_vencimiento, 20)

        cuota = Cuota(
            alumno=alumno,
            nroCuota=nro_cuota,
            año=compromiso.año,
            importe=importe,
            moraPrimerVencimiento=0,  # Inicialmente no hay mora en el primer vencimiento
            fechaPrimerVencimiento=fecha_primer_vencimiento,
            moraSegundoVencimiento=0,  # Inicialmente no hay mora en el segundo vencimiento
            fechaSegundoVencimiento=fecha_segundo_vencimiento,
            total=importe,  # Suponiendo que el total es igual al importe si no hay mora
            importePagado=0,
        )
        cuota.save()

def saldo_vencido(alumno, compromiso):
    today = now().date()
    
    # Calcula el primer día del mes actual y el último día del mes actual
    first_day_of_current_month = today.replace(day=1)
    last_day_of_current_month = (first_day_of_current_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    
    # Obtener todas las cuotas para el alumno que no están completamente pagadas
    cuotas = Cuota.objects.filter(
        alumno=alumno,
        total__gt=F('importePagado')
    )

    # Aplicar moras a todas las cuotas
    for cuota in cuotas:
        cuota.aplicar_moras(compromiso)  # Llama a aplicar_moras sin pasar el compromiso, si no es necesario

    saldo_vencido_total = 0

    for cuota in cuotas:
        # Determina el primer y último día del mes de vencimiento de la cuota
        first_day_of_due_month = cuota.fechaPrimerVencimiento.replace(day=1)
        last_day_of_due_month = (first_day_of_due_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        
        if cuota.fechaPrimerVencimiento <= last_day_of_due_month and cuota.fechaPrimerVencimiento < today:
            if today > last_day_of_due_month:
                # Si hoy es después del último día del mes de vencimiento y la cuota no está pagada, se suma al saldo vencido
                saldo_vencido_total += float(cuota.total) - cuota.importePagado

    return saldo_vencido_total

def proximo_vencimiento(alumno):
    # Filtrar las cuotas del alumno que no están completamente pagadas y que tienen vencimientos en el futuro
    proxima_cuota = Cuota.objects.filter(
        alumno=alumno,
        total__gt=F('importePagado'),  # Cuotas que no están completamente pagadas
    ).filter(
        Q(fechaPrimerVencimiento__gt=now()) | Q(fechaSegundoVencimiento__gt=now())  # Primer o segundo vencimiento en el futuro
    ).order_by(
        'fechaPrimerVencimiento', 'fechaSegundoVencimiento'  # Ordenar por la fecha de vencimiento más próxima
    ).first()  # Obtener la primera cuota con el vencimiento más cercano

    # Determinar cuál es la fecha de vencimiento más próxima
    if proxima_cuota:
        fecha_vencimiento_mas_proxima = min(
            fecha for fecha in [
                proxima_cuota.fechaPrimerVencimiento,
                proxima_cuota.fechaSegundoVencimiento
            ] if fecha > now().date()  # Considerar solo fechas en el futuro
        )
        return fecha_vencimiento_mas_proxima
    else:
        return None