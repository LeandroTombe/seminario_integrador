from django.urls import path

from .views import AlumnosCuotasVencidas,AlumnosNoPagaron2View,AlumnosCompromisoFirmadoView,CambiarEstadoPagoAPIView,AlumnosNoPagaronView,AlumnoDetailView,MateriasView,MateriaCreateView, MateriaListView, MateriaDetailView, MensajesView,PagoDeleteView,PagoListCreateView,PagoDetailView,AllPagoListView,PagoUpdateView, PagoView,ParametrosCompromisoSetValores,CompromisoActualView,AllCompromisoListView,ParametrosCompromisoEditar, FirmarCompromisoView, FirmaCompromisoActualListView, EstadoDeCuentaAlumnoView, ResumenAlumnoView,ExistenciaDeFirmaAlumnoCompromisoActualView,AllAlumnosInscriptosListView,ImportarCuotaPIView,ObtenerMateriasPorCodigoView, ObtenerPagoPorAlumnosView, InformarPagoCuotas


urlpatterns = [
    
    #materias
    path('materia/', MateriasView.as_view()),
    path('materias/', MateriaListView.as_view(), name='materia-list'),
    path('materias/create/', MateriaCreateView.as_view(), name='materia-create'),
    path('materias/<int:pk>/', MateriaDetailView.as_view(), name='materia-detail'),
    path('materiasPorCodigo/', ObtenerMateriasPorCodigoView.as_view(), name='nombre-materias-por-codigo'),
    
    #Pagos
    path('pagos/', PagoListCreateView.as_view(), name='movie-list-create'),
    path('pagos/<int:pk>/', PagoDetailView.as_view(), name='movie-detail'),
    path('pagos/all/', AllPagoListView.as_view(), name='all-movies-list'),  
    path('pagos/delete/<int:pk>/', PagoDeleteView.as_view(), name='movie-delete'), 
    path('pagos/update/<int:pk>/', PagoUpdateView.as_view(), name='movie-update'),
    path('pagos/porAlumno/', ObtenerPagoPorAlumnosView.as_view(), name='pagos-por-alumno'),
    path('pagos/informarPagoCuotas/', InformarPagoCuotas.as_view(), name='informar-pago-cuotas'),

    #Compromiso
    path('parametrosCompromiso/', ParametrosCompromisoSetValores.as_view(), name='set-valores-compromiso'),
    path('compromisoActual/', CompromisoActualView.as_view(), name='compromiso-actual'),
    path('historialCompromiso/', AllCompromisoListView.as_view(), name='historial-compromiso'),
    path('parametrosCompromisoEditar/', ParametrosCompromisoEditar.as_view(), name='editar-compromiso'),
    path('firmaCompromiso/', FirmarCompromisoView.as_view(), name='firmar-compromiso'),
    path('existenciaFirmaAlumnoCompromisoActual/', ExistenciaDeFirmaAlumnoCompromisoActualView.as_view(), name='existencia-firma-comp-acutal'),
    path('listadoFirmaCompromisoActual/', FirmaCompromisoActualListView.as_view(), name='lista-firma-compromiso-actual'),

    path('listadoAlumnosInscriptos/', AllAlumnosInscriptosListView.as_view(), name='lista-alumnos-cuatrimestre-actual'),

    #Estado de cuenta
    path('estadoDeCuentaAlumno/', EstadoDeCuentaAlumnoView.as_view(), name='estado-de-cuenta-alumno'),
    path('resumenAlumno/', ResumenAlumnoView.as_view(), name='resumenAlumno'),
    
    
    #Importacion de las cuotas
    path("importarCuotas/", ImportarCuotaPIView.as_view(), name="importar-cuotas"),
    
    #ALUMNOS
    #obtener un alumno por id
    path('alumno/perfil/', AlumnoDetailView.as_view(), name='alumno-detail'),
    path('alumno/habilitaciones',AlumnosNoPagaronView.as_view(), name='alumnos-no-pagaron'),
    path('alumno/<int:id>/cambiar-estado-pago/', CambiarEstadoPagoAPIView.as_view(), name='cambiar_estado_pago'),
    path('alumno/ihhabilitados/', AlumnosCompromisoFirmadoView.as_view(), name='comprobar-firma'),
    path('alumno/ultimacuotapagada/', AlumnosNoPagaron2View.as_view(), name='comprobar-firma'),
    path('alumno/coutasvencidas/', AlumnosCuotasVencidas.as_view(), name='comprobar-firma'),


    
    #notificaciones
    path('notificaciones/', PagoView.as_view(), name='pago'),
    path('mensajes/', MensajesView.as_view(), name='mensajes-list'),

]
