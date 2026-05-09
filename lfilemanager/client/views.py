"""
Views (ViewSets) para la API REST del sistema legal.
"""
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Rol, Usuario, TipoCaso, EstadoCaso,
    Caso, CodigoLegal, CasoNormativa, Documento
)
from .serializers import (
    RegisterSerializer, LoginSerializer, UsuarioSerializer,
    UsuarioUpdateSerializer, RolSerializer, TipoCasoSerializer,
    EstadoCasoSerializer, CasoSerializer, CasoCreateSerializer,
    CodigoLegalSerializer, CasoNormativaSerializer, DocumentoSerializer
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
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['oid_tipo_caso', 'oid_estado', 'oid_abogado']
    search_fields = ['titulo', 'numero_expediente', 'descripcion', 'juzgado']
    ordering_fields = ['fecha_inicio', 'fecha_cierre', 'titulo']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CasoCreateSerializer
        return CasoSerializer


class CodigoLegalViewSet(viewsets.ModelViewSet):
    """CRUD /api/codigos/ — Gestión de códigos legales con filtros."""
    queryset = CodigoLegal.objects.all()
    serializer_class = CodigoLegalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['vigencia']
    search_fields = ['nombre_norma', 'numero_articulo', 'texto_contenido']


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
