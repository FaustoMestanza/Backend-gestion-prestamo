from rest_framework import viewsets
from .models import Equipo
from .serializers import EquipoSerializer

class EquipoViewSet(viewsets.ModelViewSet):
    """
    Controlador REST que expone automáticamente los endpoints CRUD:
    GET, POST, PUT, PATCH, DELETE
    """
    serializer_class = EquipoSerializer

    def get_queryset(self):
        queryset = Equipo.objects.all().order_by("-fecha_registro")
        codigo = self.request.query_params.get("codigo")
        if codigo:
            queryset = queryset.filter(codigo=codigo)
        return queryset
