from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Prestamo, EstadoPrestamo
from .serializers import PrestamoSerializer
import requests
from datetime import datetime, timezone, timedelta

USUARIOS_URL = "https://microservicio-usuarios-gsbhdjavc9fjf9a8.brazilsouth-01.azurewebsites.net/api/v1/usuarios/"
INVENTARIO_URL = "https://microservicio-gestioninventario-e7byadgfgdhpfyen.brazilsouth-01.azurewebsites.net/api/equipos/"

class PrestamoViewSet(viewsets.ModelViewSet):
    queryset = Prestamo.objects.all().order_by('-fecha_inicio')
    serializer_class = PrestamoSerializer

    # ===========================================================
    #     CREAR PRÉSTAMO
    # ===========================================================
    def create(self, request, *args, **kwargs):
        data = request.data
        equipo_id = data.get("equipo_id")
        usuario_id = data.get("usuario_id")

        # Verificar si ya tiene préstamo activo
        prestamo_activo = Prestamo.objects.filter(
            usuario_id=usuario_id,
            estado=EstadoPrestamo.ABIERTO
        ).exists()

        if prestamo_activo:
            return Response(
                {"error": "El usuario ya tiene un préstamo activo"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar usuario
        try:
            user_response = requests.get(f"{USUARIOS_URL}{usuario_id}/")
            if user_response.status_code != 200:
                return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except requests.exceptions.RequestException:
            return Response({"error": "Error de conexión con microservicio usuarios"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Validar equipo
        try:
            eq_response = requests.get(f"{INVENTARIO_URL}{equipo_id}/")
            if eq_response.status_code != 200:
                return Response({"error": "Equipo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

            equipo = eq_response.json()
            if equipo.get("estado") != "Disponible":
                return Response({"error": "Equipo no disponible para préstamo"}, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException:
            return Response({"error": "Error de conexión con microservicio inventario"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Crear préstamo
        try:
            prestamo = Prestamo.objects.create(
                equipo_id=equipo_id,
                usuario_id=usuario_id,
                registrado_por_id=data.get("registrado_por_id"),
                fecha_compromiso=data.get("fecha_compromiso"),
                estado=EstadoPrestamo.ABIERTO
            )
        except Exception:
            return Response({"error": "No se pudo registrar el préstamo"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Cambiar estado del equipo
        try:
            requests.patch(f"{INVENTARIO_URL}{equipo_id}/", json={"estado": "Prestado"})
        except requests.exceptions.RequestException:
            pass

        return Response(
            {
                "mensaje": "Préstamo registrado correctamente",
                "prestamo": PrestamoSerializer(prestamo).data
            },
            status=status.HTTP_201_CREATED
        )

    # ===========================================================
    #     RETRIEVE
    # ===========================================================
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        fecha_actual = datetime.now(timezone.utc)

        if fecha_actual > instance.fecha_compromiso and instance.estado != EstadoPrestamo.VENCIDO:
            instance.estado = EstadoPrestamo.VENCIDO
            instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # ===========================================================
    #     FILTROS Y AUTOREGISTRO DE VENCIDOS EN LISTADOS
    # ===========================================================
    def get_queryset(self):
        queryset = Prestamo.objects.all().order_by('-fecha_inicio')

        # Actualizar estados vencidos automáticamente
        fecha_actual = datetime.now(timezone.utc)
        for p in queryset:
            if fecha_actual > p.fecha_compromiso and p.estado != EstadoPrestamo.VENCIDO:
                p.estado = EstadoPrestamo.VENCIDO
                p.save()

        # Filtro por docente
        docente_id = (
            self.request.headers.get('X-User-Id')
            or self.request.query_params.get('registrado_por_id')
        )
        if docente_id:
            queryset = queryset.filter(registrado_por_id=docente_id)

        # Filtro por código de equipo
        codigo = self.request.query_params.get('codigo')
        if codigo:
            try:
                resp = requests.get(f"{INVENTARIO_URL}?codigo={codigo}")
                if resp.status_code == 200:
                    equipos = resp.json()
                    if isinstance(equipos, list) and equipos:
                        equipo_id = equipos[0].get("id")
                    elif isinstance(equipos, dict):
                        equipo_id = equipos.get("id")
                    else:
                        equipo_id = None

                    queryset = queryset.filter(equipo_id=equipo_id) if equipo_id else queryset.none()
                else:
                    queryset = queryset.none()
            except:
                queryset = queryset.none()

        return queryset

    # ===========================================================
    #     🔥 ENDPOINT PERSONALIZADO: PRÉSTAMOS VENCIDOS
    # ===========================================================
    @action(detail=False, methods=['get'])
    def vencidos(self, request):
        """Devuelve préstamos vencidos con datos del alumno, equipo y docente."""
        ahora = datetime.now(timezone.utc)

        prestamos = Prestamo.objects.filter(
            fecha_compromiso__lt=ahora,
            
        )

        resultado = []

        for p in prestamos:
            

            # Alumno
            alumno = {}
            try:
                r = requests.get(f"{USUARIOS_URL}{p.usuario_id}/")
                if r.status_code == 200:
                    alumno = r.json()
            except:
                alumno = {}

            # Equipo
            equipo = {}
            try:
                r2 = requests.get(f"{INVENTARIO_URL}{p.equipo_id}/")
                if r2.status_code == 200:
                    equipo = r2.json()
            except:
                equipo = {}

            # Docente
            docente = {}
            try:
                r3 = requests.get(f"{USUARIOS_URL}{p.registrado_por_id}/")
                if r3.status_code == 200:
                    docente = r3.json()
            except:
                docente = {}

            resultado.append({
                "prestamo_id": p.id,
                "usuario_nombre": f"{alumno.get('nombre', '')} {alumno.get('apellido', '')}".strip(),
                "equipo_nombre": equipo.get("nombre", ""),
                "equipo_codigo": equipo.get("codigo", ""),
                "fecha_compromiso": p.fecha_compromiso,
                "docente_nombre": f"{docente.get('nombre', '')} {docente.get('apellido', '')}".strip(),
                "docente_token": docente.get("token_notificacion", None)
            })

        return Response(resultado)

    # ===========================================================
    #     🔥 ENDPOINT PERSONALIZADO: PRÉSTAMOS POR VENCER
    # ===========================================================
    @action(detail=False, methods=['get'])
    def por_vencer(self, request):
        """Préstamos que vencerán dentro de 24 horas."""
        ahora = datetime.now(timezone.utc)
        mañana = ahora + timedelta(days=1)

        prestamos = Prestamo.objects.filter(
            fecha_compromiso__date=mañana.date(),
            estado=EstadoPrestamo.ABIERTO
        )

        resultado = []

        for p in prestamos:
            alumno = {}
            try:
                r = requests.get(f"{USUARIOS_URL}{p.usuario_id}/")
                if r.status_code == 200:
                    alumno = r.json()
            except:
                alumno = {}

            equipo = {}
            try:
                r2 = requests.get(f"{INVENTARIO_URL}{p.equipo_id}/")
                if r2.status_code == 200:
                    equipo = r2.json()
            except:
                equipo = {}

            resultado.append({
                "prestamo_id": p.id,
                "usuario_id": p.usuario_id,
                "usuario_nombre": f"{alumno.get('nombre', '')} {alumno.get('apellido', '')}".strip(),
                "equipo_nombre": equipo.get("nombre", ""),
                "fecha_compromiso": p.fecha_compromiso,
                "token_notificacion": alumno.get("token_notificacion", None)
            })

        return Response(resultado)
