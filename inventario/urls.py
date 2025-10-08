from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquipoViewSet

router = DefaultRouter()
router.register(r'equipos', EquipoViewSet)  # Crea las rutas automáticamente

urlpatterns = [
    path('', include(router.urls)),
]
