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

    # Dar de alta la matricula
    if not Cuota.objects.filter(alumno=alumno, año=compromiso.año, nroCuota=0).exists():
        fecha_primer_vencimiento = datetime(compromiso.año, 8, 10)
        fecha_segundo_vencimiento = datetime(compromiso.año, 8, 20)

        cuota = Cuota(
            alumno=alumno,
            nroCuota=0,
            año=compromiso.año,
            importe=compromiso.importe_matricula,
            moraPrimerVencimiento=0,  # Inicialmente no hay mora en el primer vencimiento
            fechaPrimerVencimiento=fecha_primer_vencimiento,
            moraSegundoVencimiento=0,  # Inicialmente no hay mora en el segundo vencimiento
            fechaSegundoVencimiento=fecha_segundo_vencimiento,
            total=compromiso.importe_matricula,  # Suponiendo que el total es igual al importe si no hay mora
            importePagado=0,
            importeInformado=0,
            fechaImporteInformado=fecha_primer_vencimiento,
        )
        cuota.save()

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
            importeInformado=0,
            fechaImporteInformado=fecha_primer_vencimiento,
        )
        cuota.save()

def saldo_vencido(alumno, compromiso):
    today = now().date()

    # Obtener todas las cuotas para el alumno que no están completamente pagadas
    cuotas = Cuota.objects.filter(
        alumno=alumno,
        total__gt=F('importePagado')
    )

    # Aplicar moras a todas las cuotas
    for cuota in cuotas:
        cuota.aplicar_moras(compromiso)

    saldo_vencido_total = 0

    for cuota in cuotas:
        # Si la cuota está vencida (fechaPrimerVencimiento es anterior a hoy) y no está pagada completamente
        if cuota.fechaPrimerVencimiento < today:
            # Sumar el saldo vencido de esta cuota
            saldo_vencido_total += (cuota.total - cuota.importePagado)

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