from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Prestamo, EstadoPrestamo
from .serializers import PrestamoSerializer
import requests

# 🌐 URLs de microservicios
USUARIOS_URL = "https://microservicio-usuarios-gsbhdjavc9fjf9a8.brazilsouth-01.azurewebsites.net/api/v1/usuarios/"
INVENTARIO_URL = "https://microservicio-gestioninventario-e7byadgfgdhpfyen.brazilsouth-01.azurewebsites.net/api/equipos/"

class PrestamoViewSet(viewsets.ModelViewSet):
    """
    CRUD completo para gestión de préstamos.
    Valida usuario y equipo antes de crear el préstamo y actualiza el estado del equipo.
    """
    queryset = Prestamo.objects.all().order_by('-fecha_inicio')
    serializer_class = PrestamoSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        equipo_id = data.get("equipo_id")
        usuario_id = data.get("usuario_id")

        print("==== CREACIÓN DE PRÉSTAMO ====")
        print("Datos recibidos:", data)

        #  Verificar si el usuario ya tiene un préstamo activo
        prestamo_activo = Prestamo.objects.filter(
            usuario_id=usuario_id,
            estado=EstadoPrestamo.ABIERTO
        ).exists()

        if prestamo_activo:
            print("⚠️ Usuario ya tiene un préstamo activo")
            return Response(
                {"error": "El usuario ya tiene un préstamo activo"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar usuario
        try:
            user_response = requests.get(f"{USUARIOS_URL}{usuario_id}/")
            print("USUARIO RESP:", user_response.status_code)
            if user_response.status_code != 200:
                return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except requests.exceptions.RequestException as e:
            print(" Error conexión usuarios:", e)
            return Response({"error": "Error de conexión con microservicio usuarios"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Validar equipo
        try:
            eq_response = requests.get(f"{INVENTARIO_URL}{equipo_id}/")
            print("EQUIPO RESP:", eq_response.status_code)
            if eq_response.status_code != 200:
                return Response({"error": "Equipo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

            equipo = eq_response.json()
            if equipo.get("estado") != "Disponible":
                print("⚠️ Equipo no disponible:", equipo.get("estado"))
                return Response({"error": "Equipo no disponible para préstamo"}, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException as e:
            print("Error conexión inventario:", e)
            return Response({"error": "Error de conexión con microservicio inventario"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 🔹 Crear el préstamo
        try:
            prestamo = Prestamo.objects.create(
                equipo_id=equipo_id,
                usuario_id=usuario_id,
                registrado_por_id=data.get("registrado_por_id"),
                fecha_compromiso=data.get("fecha_compromiso"),
                estado=EstadoPrestamo.ABIERTO
            )
            print("Préstamo guardado en DB con ID:", prestamo.id)
        except Exception as e:
            print("Error al guardar préstamo:", e)
            return Response({"error": "No se pudo registrar el préstamo"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 🔹 Cambiar estado del equipo a “Prestado”
        try:
            patch_resp = requests.patch(f"{INVENTARIO_URL}{equipo_id}/", json={"estado": "Prestado"})
            print("PATCH inventario:", patch_resp.status_code, patch_resp.text)
        except requests.exceptions.RequestException as e:
            print("⚠️ Error actualizando estado del equipo:", e)

        print("==== FIN DE CREACIÓN ====")

        # 🔹 Respuesta final
        return Response(
            {
                "mensaje": "Préstamo registrado correctamente",
                "prestamo": PrestamoSerializer(prestamo).data
            },
            status=status.HTTP_201_CREATED
        )
    
    def get_queryset(self):
        """
        Permite listar solo los préstamos del docente autenticado flutter
        (desde Gateway o Flutter).
        """
        queryset = Prestamo.objects.all().order_by('-fecha_inicio')

        docente_id = (
            self.request.headers.get('X-User-Id')
            or self.request.query_params.get('registradoPor_id')
        )

        if docente_id:
            queryset = queryset.filter(registrado_por_id=docente_id)
               
        return queryset   
               
    