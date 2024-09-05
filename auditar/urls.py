from django.urls import path
from .views import AuditoriaListView

urlpatterns = [
    path('auditoria/', AuditoriaListView.as_view(), name='auditoria-list'),
]