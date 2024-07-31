from django.urls import path

from .views import MateriasView,MateriaCreateView, MateriaListView, MateriaDetailView


urlpatterns = [
    path('materia/', MateriasView.as_view()),
    path('materias/', MateriaListView.as_view(), name='materia-list'),
    path('materias/create/', MateriaCreateView.as_view(), name='materia-create'),
    path('materias/<int:pk>/', MateriaDetailView.as_view(), name='materia-detail'),
]
