"""Views for the Legal File Manager API.

Covers authentication, user management, case management, legal codes,
documents, payments, plans, notifications and PDF reporting.
"""
import random

from django.contrib.auth import authenticate
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import Q
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Caso, CasoNormativa, CodigoLegal, Documento,
    EstadoCaso, Notificacion, Pago, Plan,
    Rol, TipoCaso, Usuario,
)
from .serializers import (
    CasoCreateSerializer, CasoNormativaSerializer, CasoSerializer,
    CodigoLegalListSerializer, CodigoLegalSerializer,
    DocumentoSerializer, EstadoCasoSerializer,
    LoginSerializer, NotificacionSerializer,
    PagoSerializer, PlanSerializer,
    RegisterSerializer, RolSerializer,
    TipoCasoSerializer, UsuarioSerializer, UsuarioUpdateSerializer,
)


# ============================================================
# Auth Views
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """POST /api/auth/register/ — Registrar un nuevo usuario."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['rol'] = user.oid_rol.nombre if user.oid_rol else 'Básico'
        return Response({
            'user': UsuarioSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """POST /api/auth/login/ — Login con email y password, retorna JWT."""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.estado:
            return Response(
                {'error': 'Cuenta desactivada. Contacte al administrador.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['rol'] = user.oid_rol.nombre if user.oid_rol else 'Básico'

        return Response({
            'user': UsuarioSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """GET /api/auth/me/ — Retorna info del usuario autenticado."""
    # Extraer user_id del token
    user_id = request.auth.get('user_id') if request.auth else None
    if not user_id:
        return Response(
            {'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        user = Usuario.objects.select_related('oid_rol').get(
            oid_usuario=user_id)
    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND)

    return Response(UsuarioSerializer(user).data)


# ============================================================
# ViewSets — CRUD completo con filtros
# ============================================================

class RolViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/roles/ — Listar roles disponibles."""

    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]


class UsuarioViewSet(viewsets.ModelViewSet):
    """CRUD /api/usuarios/ — Gestión de usuarios (solo Admin)."""

    queryset = Usuario.objects.select_related('oid_rol').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['oid_rol', 'estado']
    search_fields = ['nombre', 'email']

    def get_serializer_class(self):
        """Return update serializer for write actions,
          full serializer otherwise."""
        if self.action in ['update', 'partial_update']:
            return UsuarioUpdateSerializer
        return UsuarioSerializer


class TipoCasoViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/tipos-caso/ — Listar tipos de caso."""

    queryset = TipoCaso.objects.all()
    serializer_class = TipoCasoSerializer
    permission_classes = [IsAuthenticated]


class EstadoCasoViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/estados-caso/ — Listar estados de caso."""

    queryset = EstadoCaso.objects.all()
    serializer_class = EstadoCasoSerializer
    permission_classes = [IsAuthenticated]


class CasoViewSet(viewsets.ModelViewSet):
    """CRUD /api/casos/ — Gestión de casos 
    legales con filtros (Aislamiento de Datos)."""

    queryset = Caso.objects.select_related(
        'oid_abogado', 'oid_tipo_caso', 'oid_estado'
    ).all()
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['oid_tipo_caso', 'oid_estado', 'oid_abogado']
    search_fields = ['titulo', 'numero_expediente', 'descripcion', 'juzgado']
    ordering_fields = ['fecha_inicio', 'fecha_cierre', 'titulo']

    # ============================================================
    # CAMBIO IMPLEMENTADO: Row-Level Security
    # ============================================================
    def get_queryset(self):
        """Filtra los casos para que los usuarios solo accedan a los suyos.

        Excepción: los Administradores ven todos los casos para auditorías.
        """
        user = self.request.user
        # Si el usuario es Administrador, mantenemos el queryset completo para auditorías
        if user.oid_rol and user.oid_rol.nombre == 'Administrador':
            return self.queryset
        # Si es un Abogado estándar, filtramos por la relación correcta (oid_abogado)
        return self.queryset.filter(oid_abogado=user)
    # ============================================================

    def get_serializer_class(self):
        """Return creation serializer for write 
        actions, full serializer otherwise."""
        if self.action in ['create', 'update', 'partial_update']:
            return CasoCreateSerializer
        return CasoSerializer

    def perform_create(self, serializer):
        """Crear caso y automáticamente crear documento si se envía PDF."""
        archivo_pdf = self.request.FILES.get('archivo_pdf')
        caso = serializer.save()

        if archivo_pdf:
            nombre_archivo = archivo_pdf.name.rsplit('.', 1)[0]
            Documento.objects.create(
                oid_caso=caso,
                nombre_archivo=nombre_archivo,
                ruta_archivo=archivo_pdf,
                tipo_documento='Documento Principal'
            )

    @action(detail=True, methods=['get'], url_path='descargar-documento')
    def descargar_documento(self, request, pk=None):  # pylint: disable=unused-argument
        """GET /api/casos/{id}/descargar-documento/ — 
        Descargar documento principal del caso."""
        caso = self.get_object()

        documento = Documento.objects.filter(
            oid_caso=caso,
            tipo_documento='Documento Principal'
        ).first()

        if not documento or not documento.ruta_archivo:
            return Response(
                {'error': 'No hay documento disponible para descargar'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            response = FileResponse(
                documento.ruta_archivo.open('rb'),
                content_type='application/pdf'
            )
            filename = documento.nombre_archivo or f"caso_{caso.oid_caso}"
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except FileNotFoundError:
            return Response(
                {'error': 'El archivo no se encuentra en el servidor'},
                status=status.HTTP_404_NOT_FOUND
            )
        except (OSError, RuntimeError) as exc:
            return Response(
                {'error': f'Error al descargar: {str(exc)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CodigoLegalViewSet(viewsets.ModelViewSet):
    """CRUD /api/codigos/ — Gestión de códigos legales con filtros."""

    queryset = CodigoLegal.objects.all()
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['vigencia']
    search_fields = ['nombre_norma', 'numero_articulo', 'texto_contenido']

    def get_serializer_class(self):
        """Return list serializer for list action, full serializer otherwise."""
        if self.action == 'list':
            return CodigoLegalListSerializer
        return CodigoLegalSerializer

    @action(detail=True, methods=['get'], url_path='descargar-documento')
    def descargar_documento(self, request, pk=None):  # pylint: disable=unused-argument
        """GET /api/codigos/{id}/descargar-documento/
          — Descargar archivo PDF del código legal."""
        codigo = self.get_object()

        if not codigo.archivo_pdf:
            return Response(
                {'error': 'No hay documento disponible para descargar'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            response = FileResponse(
                codigo.archivo_pdf.open('rb'),
                content_type='application/pdf'
            )
            filename = codigo.nombre_norma or f"codigo_{codigo.oid_codigo}"
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except FileNotFoundError:
            return Response(
                {'error': 'El archivo no se encuentra en el servidor'},
                status=status.HTTP_404_NOT_FOUND
            )
        except (OSError, RuntimeError) as exc:
            return Response(
                {'error': f'Error al descargar: {str(exc)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CasoNormativaViewSet(viewsets.ModelViewSet):
    """CRUD /api/caso-normativas/ — Asociar códigos legales a casos."""

    queryset = CasoNormativa.objects.select_related(
        'oid_caso', 'oid_codigo'
    ).order_by('-fecha_asociacion')
    serializer_class = CasoNormativaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['oid_caso', 'oid_codigo']

    def get_queryset(self):
        """Aísla las asociaciones por dueño del caso.

        El Administrador ve todas; un abogado solo las de sus propios casos.
        """
        user = self.request.user
        if user.oid_rol and user.oid_rol.nombre == 'Administrador':
            return self.queryset
        return self.queryset.filter(oid_caso__oid_abogado=user)

    def perform_create(self, serializer):
        """Impide asociar normativas a casos que no pertenecen al usuario."""
        user = self.request.user
        caso = serializer.validated_data.get('oid_caso')
        is_admin = bool(user.oid_rol and user.oid_rol.nombre == 'Administrador')
        if not is_admin and caso and caso.oid_abogado_id != user.oid_usuario:
            raise PermissionDenied('No puede asociar normativas a un caso que no le pertenece.')
        serializer.save()


class DocumentoViewSet(viewsets.ModelViewSet):
    """CRUD /api/documentos/ — Gestión de documentos PDF."""

    queryset = Documento.objects.select_related('oid_caso').all()
    serializer_class = DocumentoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['oid_caso', 'tipo_documento']


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/planes/ — Listar planes disponibles."""

    queryset = Plan.objects.filter(estado=True)
    serializer_class = PlanSerializer
    permission_classes = [AllowAny]


class PagoViewSet(viewsets.ModelViewSet):
    """CRUD /api/pagos/ — Gestión de pagos."""

    queryset = Pago.objects.select_related('oid_usuario', 'oid_plan').all()
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['oid_usuario', 'oid_plan', 'estado_pago']

    def get_queryset(self):
        """Usuarios solo ven sus propios pagos; el admin ve todos."""
        user = self.request.user
        if user.oid_rol and user.oid_rol.nombre == 'Administrador':
            return self.queryset
        return self.queryset.filter(oid_usuario=user)

    def perform_create(self, serializer):
        """Guardar el pago y crear notificación in-app para el usuario."""
        user = self.request.user
        pago = serializer.save(oid_usuario=user)

        # Crear notificación in-app para el usuario sobre el pago
        mensaje_notif = (
            f"Estimado(a) {user.nombre or 'usuario'}, hemos recibido su solicitud "
            f"para suscribirse al plan '{pago.oid_plan.nombre}' por un valor de "
            f"${pago.monto}. Un representante de nuestro equipo le contactará "
            f"próximamente al correo electrónico '{user.email}' (o puede escribirnos "
            f"a pagos@legalfilemanager.com) para coordinar el pago correspondiente "
            f"y activar todas sus funciones premium."
        )
        Notificacion.objects.create(
            oid_usuario=user,
            titulo=f"Solicitud de suscripción al Plan {pago.oid_plan.nombre}",
            mensaje=mensaje_notif,
            tipo="in-app",
            leida=False
        )


class NotificacionViewSet(viewsets.ModelViewSet):
    """CRUD /api/notificaciones/ — Sistema de notificaciones."""

    queryset = Notificacion.objects.select_related('oid_usuario').all()
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['leida', 'tipo', 'oid_usuario']

    def get_queryset(self):
        """Admin ve todas; usuarios solo ven las suyas o las globales (sin destinatario)."""
        user = self.request.user
        if user.oid_rol and user.oid_rol.nombre == 'Administrador':
            return self.queryset
        # Users see notifications targeted to them OR global notifications (oid_usuario is null)
        return self.queryset.filter(Q(oid_usuario=user) | Q(oid_usuario__isnull=True))

    def perform_create(self, serializer):
        """Admin crea notificaciones globales; otros usuarios crean las suyas."""
        user = self.request.user
        if user.oid_rol and user.oid_rol.nombre == 'Administrador':
            # Admin-created notifications are global (para todos)
            serializer.save(oid_usuario=None)
        else:
            serializer.save(oid_usuario=user)


class RequestPasswordResetView(APIView):
    """POST /api/auth/password-reset-request/ — Enviar OTP de recuperación de contraseña."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Generar y enviar un código OTP de 6 dígitos al correo registrado."""
        email = request.data.get('email')
        if not email:
            return Response(
                {"error": "El correo es requerido."}, 
                status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Usuario.objects.get(email=email, estado=True)

            # 1. Generamos el código de 6 dígitos
            codigo_otp = f"{random.randint(100000, 999999)}"

            # 2. Lo guardamos en el cache usando el email como llave.
            # timeout=900 significa 15 minutos (900 segundos). Se borrará SOLO.
            cache.set(f"recovery_{email}", codigo_otp, timeout=900)

            # 3. Enviamos el correo
            asunto = "Código de Recuperación - Sistema de Gestión Legal"
            mensaje = (
                f"Hola {user.nombre},\n\n"
                f"Tu código de verificación es: {codigo_otp}\n\n"
                f"Expira en 15 minutos."
            )

            send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [user.email])

        except Usuario.DoesNotExist:
            # Seguridad: no revelar si el correo existe o no
            pass

        return Response(
            {"message": "Código enviado si el correo existe."}, 
            status=status.HTTP_200_OK)


class ConfirmPasswordResetView(APIView):
    """POST /api/auth/password-reset-confirm/ 
    — Confirmar OTP y actualizar contraseña."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validar el OTP y cambiar la contraseña del usuario."""
        email = request.data.get('email')
        codigo = request.data.get('codigo')
        password = request.data.get('password')

        if not all([email, codigo, password]):
            return Response(
                {"error": "Todos los campos son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Recuperamos el código que guardamos en el cache
        codigo_guardado = cache.get(f"recovery_{email}")

        # 2. Si no existe (porque ya pasaron 15 min) o no coincide, rebotamos
        if not codigo_guardado or codigo_guardado != str(codigo):
            return Response(
                {"error": "El código es inválido o ha expirado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = Usuario.objects.get(email=email)

            # 3. Todo está bien, cambiamos la contraseña
            user.set_password(password)
            user.save()

            # 4. Borramos el código del cache para que no se pueda reutilizar
            cache.delete(f"recovery_{email}")

            return Response(
                {"message": "Contraseña actualizada con éxito."},
                status=status.HTTP_200_OK
            )
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )


# ============================================================
# Extra Functional Endpoints (Auth & Reports)
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_view(request):
    """POST /api/auth/password-reset/ — Mock de reset de contraseña."""
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email es requerido'}, status=status.HTTP_400_BAD_REQUEST)
    # Aquí iría la lógica de envío de email
    return Response({'message': f'Se ha enviado un enlace de recuperación a {email}'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa_view(request):
    """POST /api/auth/2fa/verify/ — Mock de verificación 2FA."""
    code = request.data.get('code')
    if code == "123456":  # Mock validation
        return Response({'status': 'verified'})
    return Response({'error': 'Código inválido'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generar_reporte_pdf_view(request, caso_id):  # pylint: disable=unused-argument
    """GET /api/reportes/caso/{id}/pdf/ — Mock de generación de PDF."""
    try:
        caso = Caso.objects.get(oid_caso=caso_id)
        # Mock de respuesta PDF
        return Response({
            'message': f'Generando reporte PDF para el caso {caso.numero_expediente}',
            'download_url': f'/media/reports/caso_{caso_id}.pdf'
        })
    except Caso.DoesNotExist:
        return Response(
            {'error': 'Caso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
