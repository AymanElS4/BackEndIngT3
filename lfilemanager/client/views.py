"""
Views (ViewSets) para la API REST del sistema legal.
"""
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse

from .models import (
    Rol, Usuario, TipoCaso, EstadoCaso,
    Caso, CodigoLegal, CasoNormativa, Documento,
    Plan, Pago, Notificacion
)
from .serializers import (
    RegisterSerializer, LoginSerializer, UsuarioSerializer,
    UsuarioUpdateSerializer, RolSerializer, TipoCasoSerializer,
    EstadoCasoSerializer, CasoSerializer, CasoCreateSerializer,
    CodigoLegalListSerializer, CodigoLegalSerializer, CasoNormativaSerializer, DocumentoSerializer,
    PlanSerializer, PagoSerializer, NotificacionSerializer
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
        refresh = RefreshToken()
        refresh['user_id'] = user.oid_usuario
        refresh['email'] = user.email
        refresh['rol'] = user.oid_rol.nombre
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

        from django.contrib.auth import authenticate
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
        refresh = RefreshToken()
        refresh['user_id'] = user.oid_usuario
        refresh['email'] = user.email
        refresh['rol'] = user.oid_rol.nombre

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
        return Response({'error': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        user = Usuario.objects.select_related('oid_rol').get(oid_usuario=user_id)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

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
    """CRUD /api/casos/ — Gestión de casos legales con filtros."""
    queryset = Caso.objects.select_related(
        'oid_abogado', 'oid_tipo_caso', 'oid_estado'
    ).all()
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['oid_tipo_caso', 'oid_estado', 'oid_abogado']
    search_fields = ['titulo', 'numero_expediente', 'descripcion', 'juzgado']
    ordering_fields = ['fecha_inicio', 'fecha_cierre', 'titulo']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CasoCreateSerializer
        return CasoSerializer
    
    def perform_create(self, serializer):
        """Crear caso y automáticamente crear documento si se envía PDF."""
        # Extraer el archivo PDF del request
        archivo_pdf = self.request.FILES.get('archivo_pdf')
        
        # Guardar el caso
        caso = serializer.save()
        
        # Si hay PDF, crear documento automáticamente
        if archivo_pdf:
            nombre_archivo = archivo_pdf.name.rsplit('.', 1)[0]  # Remove .pdf extension
            Documento.objects.create(
                oid_caso=caso,
                nombre_archivo=nombre_archivo,
                ruta_archivo=archivo_pdf,
                tipo_documento='Documento Principal'
            )
    
    @action(detail=True, methods=['get'], url_path='descargar-documento')
    def descargar_documento(self, request, pk=None):
        """GET /api/casos/{id}/descargar-documento/ — Descargar documento principal del caso."""
        caso = self.get_object()
        
        # Obtener el documento principal del caso
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
            file_path = documento.ruta_archivo.path
            response = FileResponse(
                open(file_path, 'rb'),
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
        except Exception as e:
            return Response(
                {'error': f'Error al descargar: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CodigoLegalViewSet(viewsets.ModelViewSet):
    """CRUD /api/codigos/ — Gestión de códigos legales con filtros."""
    queryset = CodigoLegal.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['vigencia']
    search_fields = ['nombre_norma', 'numero_articulo', 'texto_contenido']

    def get_serializer_class(self):
        if self.action == 'list':
            return CodigoLegalListSerializer
        return CodigoLegalSerializer


class CasoNormativaViewSet(viewsets.ModelViewSet):
    """CRUD /api/caso-normativas/ — Asociar códigos legales a casos."""
    queryset = CasoNormativa.objects.select_related('oid_caso', 'oid_codigo').all()
    serializer_class = CasoNormativaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['oid_caso', 'oid_codigo']


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
        # Usuarios solo ven sus propios pagos, admin ve todos
        user = self.request.user
        if user.oid_rol and user.oid_rol.nombre == 'Administrador':
            return self.queryset
        return self.queryset.filter(oid_usuario=user)


class NotificacionViewSet(viewsets.ModelViewSet):
    """CRUD /api/notificaciones/ — Sistema de notificaciones."""
    queryset = Notificacion.objects.select_related('oid_usuario').all()
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['leida', 'tipo', 'oid_usuario']

    def get_queryset(self):
        from django.db.models import Q
        user = self.request.user
        if user.oid_rol and user.oid_rol.nombre == 'Administrador':
            return self.queryset
        # Users see notifications targeted to them OR global notifications (oid_usuario is null)
        return self.queryset.filter(Q(oid_usuario=user) | Q(oid_usuario__isnull=True))

    def perform_create(self, serializer):
        user = self.request.user
        if user.oid_rol and user.oid_rol.nombre == 'Administrador':
            # Admin-created notifications are global (para todos)
            serializer.save(oid_usuario=None)
        else:
            serializer.save(oid_usuario=user)


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
    if code == "123456": # Mock validation
        return Response({'status': 'verified'})
    return Response({'error': 'Código inválido'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generar_reporte_pdf_view(request, caso_id):
    """GET /api/reportes/caso/{id}/pdf/ — Mock de generación de PDF."""
    try:
        caso = Caso.objects.get(oid_caso=caso_id)
        # Mock de respuesta PDF
        return Response({
            'message': f'Generando reporte PDF para el caso {caso.numero_expediente}',
            'download_url': f'/media/reports/caso_{caso_id}.pdf'
        })
    except Caso.DoesNotExist:
        return Response({'error': 'Caso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
