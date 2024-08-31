from django.urls import path

from .views import MateriasView,MateriaCreateView, MateriaListView, MateriaDetailView,PagoDeleteView,PagoListCreateView,PagoDetailView,AllPagoListView,PagoUpdateView,ParametrosCompromisoSetValores,CompromisoActualView,AllCompromisoListView,ParametrosCompromisoEditar, FirmarCompromisoView, FirmaCompromisoActualListView, EstadoDeCuentaAlumnoView, ResumenAlumnoView,ExistenciaDeFirmaAlumnoCompromisoActualView


urlpatterns = [
    
    #materias
    path('materia/', MateriasView.as_view()),
    path('materias/', MateriaListView.as_view(), name='materia-list'),
    path('materias/create/', MateriaCreateView.as_view(), name='materia-create'),
    path('materias/<int:pk>/', MateriaDetailView.as_view(), name='materia-detail'),
    
    #Pagos
    path('pagos/', PagoListCreateView.as_view(), name='movie-list-create'),
    path('pagos/<int:pk>/', PagoDetailView.as_view(), name='movie-detail'),
    path('pagos/all/', AllPagoListView.as_view(), name='all-movies-list'),  
    path('pagos/delete/<int:pk>/', PagoDeleteView.as_view(), name='movie-delete'), 
    path('pagos/update/<int:pk>/', PagoUpdateView.as_view(), name='movie-update'),

    #Compromiso
    path('parametrosCompromiso/', ParametrosCompromisoSetValores.as_view(), name='set-valores-compromiso'),
    path('compromisoActual/', CompromisoActualView.as_view(), name='compromiso-actual'),
    path('historialCompromiso/', AllCompromisoListView.as_view(), name='historial-compromiso'),
    path('parametrosCompromisoEditar/', ParametrosCompromisoEditar.as_view(), name='editar-compromiso'),
    path('firmaCompromiso/', FirmarCompromisoView.as_view(), name='firmar-compromiso'),
    path('existenciaFirmaAlumnoCompromisoActual/', ExistenciaDeFirmaAlumnoCompromisoActualView.as_view(), name='existencia-firma-comp-acutal'),
    path('listadoFirmaCompromisoActual/', FirmaCompromisoActualListView.as_view(), name='lista-firma-compromiso-actual'),

    #Estado de cuenta
    path('estadoDeCuentaAlumno/', EstadoDeCuentaAlumnoView.as_view(), name='estado-de-cuenta-alumno'),
    path('resumenAlumno/', ResumenAlumnoView.as_view(), name='resumenAlumno'),
]
