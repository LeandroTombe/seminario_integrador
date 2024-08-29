from .models import Cuota
from datetime import datetime, timedelta

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
        # Calcular la fecha de vencimiento como el día 10 del mes de la cuota
        mes_vencimiento = nro_cuota
        año_vencimiento = compromiso.año

        fecha_vencimiento = datetime(año_vencimiento, mes_vencimiento, 10)

        cuota = Cuota(
            alumno=alumno,
            nroCuota=nro_cuota,
            año=compromiso.año,
            importe=importe,
            mora=0,
            total=importe,  # Suponiendo que el total es igual al importe si no hay mora
            fechaVencimiento=fecha_vencimiento,
            importePagado=0,
        )
        cuota.save()