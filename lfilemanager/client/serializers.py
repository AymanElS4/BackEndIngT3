"""
Serializers para la API REST del sistema legal.
"""
# pylint: disable=too-few-public-methods
import filetype  
from rest_framework import serializers  
from .models import (
    Rol, Usuario, TipoCaso, EstadoCaso,
    Caso, CodigoLegal, CasoNormativa, Documento,
    Plan, Pago, Notificacion
)


# ============================================================
# Auth Serializers
# ============================================================

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de nuevos usuarios."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        """Metaclase de RegisterSerializer."""
        model = Usuario
        fields = [
            'oid_usuario', 'nombre', 'email', 'password',
            'matricula_profesional', 'especialidad', 'telefono_contacto'
        ]
        read_only_fields = ['oid_usuario']
        extra_kwargs = {
            'matricula_profesional': {'required': False},
            'especialidad': {'required': False},
            'telefono_contacto': {'required': False},
        }

    def create(self, validated_data):
        """Crea un nuevo usuario con rol básico y contraseña hasheada."""
        rol_basico, _ = Rol.objects.get_or_create(
            nombre='Básico',
            defaults={'descripcion': 'Usuario con acceso básico'}
        )
        password = validated_data.pop('password')
        user = Usuario.objects.create_user(
            password=password,
            oid_rol=rol_basico,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer para login."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer completo de Usuario (lectura)."""
    rol_nombre = serializers.CharField(source='oid_rol.nombre', read_only=True)

    class Meta:
        """Metaclase de UsuarioSerializer."""
        model = Usuario
        fields = [
            'oid_usuario', 'nombre', 'email', 'oid_rol', 'rol_nombre',
            'fecha_registro', 'estado', 'matricula_profesional',
            'especialidad', 'telefono_contacto'
        ]
        read_only_fields = ['oid_usuario', 'fecha_registro']


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar usuario (Admin)."""
    class Meta:
        """Metaclase de UsuarioUpdateSerializer."""
        model = Usuario
        fields = [
            'nombre', 'email', 'oid_rol', 'estado',
            'matricula_profesional', 'especialidad', 'telefono_contacto'
        ]


# ============================================================
# Domain Serializers
# ============================================================

class RolSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Rol."""
    class Meta:
        """Metaclase de RolSerializer."""
        model = Rol
        fields = '__all__'


class TipoCasoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo TipoCaso."""
    class Meta:
        """Metaclase de TipoCasoSerializer."""
        model = TipoCaso
        fields = '__all__'


class EstadoCasoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo EstadoCaso."""
    class Meta:
        """Metaclase de EstadoCasoSerializer."""
        model = EstadoCaso
        fields = '__all__'


class CasoSerializer(serializers.ModelSerializer):
    """Serializer para Caso con datos expandidos."""
    abogado_nombre = serializers.CharField(source='oid_abogado.nombre', read_only=True)
    tipo_caso_nombre = serializers.CharField(source='oid_tipo_caso.nombre', read_only=True)
    estado_nombre = serializers.CharField(source='oid_estado.nombre', read_only=True)
    documentos_count = serializers.IntegerField(source='documentos.count', read_only=True)

    class Meta:
        """Metaclase de CasoSerializer."""
        model = Caso
        fields = [
            'oid_caso', 'oid_abogado', 'abogado_nombre',
            'oid_tipo_caso', 'tipo_caso_nombre',
            'oid_estado', 'estado_nombre',
            'titulo', 'descripcion', 'numero_expediente',
            'fecha_inicio', 'fecha_cierre', 'juzgado',
            'documentos_count'
        ]
        read_only_fields = ['oid_caso']


class CasoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear/editar un Caso con PDF."""
    archivo_pdf = serializers.FileField(required=False, allow_null=True, write_only=True)

    class Meta:
        """Metaclase de CasoCreateSerializer."""
        model = Caso
        fields = [
            'oid_abogado', 'oid_tipo_caso', 'oid_estado',
            'titulo', 'descripcion', 'numero_expediente',
            'fecha_inicio', 'fecha_cierre', 'juzgado', 'archivo_pdf'
        ]

    def validate_archivo_pdf(self, value):
        """Valida que el archivo adjunto sea un PDF válido y no supere 50 MB."""
        if value is None:
            return value

        header = value.read(261)
        value.seek(0)
        kind = filetype.guess(header)
        if kind is None or kind.mime != 'application/pdf':
            detected = kind.mime if kind else 'desconocido'
            raise serializers.ValidationError(
                f"El archivo no es un PDF válido (tipo detectado: {detected}). "
                "Solo se permiten archivos PDF."
            )

        max_size = 50 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"El archivo es demasiado grande. Máximo: 50 MB. "
                f"Tu archivo: {value.size / (1024 * 1024):.2f} MB"
            )

        return value

    def create(self, validated_data):
        """Crea el Caso descartando el archivo PDF, que se gestiona por separado."""
        validated_data.pop('archivo_pdf', None)
        caso = Caso.objects.create(**validated_data)
        return caso


class CodigoLegalListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados.

    Omite texto_contenido para no transferir cientos de KB por request.
    """
    estado_vigencia = serializers.SerializerMethodField()

    class Meta:
        """Metaclase de CodigoLegalListSerializer."""
        model = CodigoLegal
        fields = ['oid_codigo', 'nombre_norma', 'numero_articulo', 'vigencia', 'estado_vigencia']
        read_only_fields = ['oid_codigo']

    def get_estado_vigencia(self, obj):
        """Retorna la etiqueta de vigencia legible."""
        return 'Vigente' if obj.vigencia else 'Histórico'


class CodigoLegalSerializer(serializers.ModelSerializer):
    """Serializer completo para create/retrieve/update — incluye texto_contenido."""
    estado_vigencia = serializers.SerializerMethodField()

    class Meta:
        """Metaclase de CodigoLegalSerializer."""
        model = CodigoLegal
        fields = [
            'oid_codigo', 'nombre_norma', 'numero_articulo',
            'texto_contenido', 'vigencia', 'estado_vigencia'
        ]
        read_only_fields = ['oid_codigo']

    def get_estado_vigencia(self, obj):
        """Retorna la etiqueta de vigencia legible."""
        return 'Vigente' if obj.vigencia else 'Histórico'


class CasoNormativaSerializer(serializers.ModelSerializer):
    """Serializer para la relación entre Caso y CodigoLegal."""
    codigo_nombre = serializers.CharField(source='oid_codigo.nombre_norma', read_only=True)
    caso_titulo = serializers.CharField(source='oid_caso.titulo', read_only=True)

    class Meta:
        """Metaclase de CasoNormativaSerializer."""
        model = CasoNormativa
        fields = [
            'oid_relacion', 'oid_caso', 'caso_titulo',
            'oid_codigo', 'codigo_nombre', 'fecha_asociacion'
        ]
        read_only_fields = ['oid_relacion', 'fecha_asociacion']


class DocumentoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Documento."""
    class Meta:
        """Metaclase de DocumentoSerializer."""
        model = Documento
        fields = [
            'oid_documento', 'oid_caso', 'nombre_archivo',
            'ruta_archivo', 'tipo_documento', 'fecha_subida'
        ]
        read_only_fields = ['oid_documento', 'fecha_subida']

    def validate_ruta_archivo(self, value):
        """Valida que el archivo subido sea un PDF válido y no supere 50 MB."""
        header = value.read(261)
        value.seek(0)
        kind = filetype.guess(header)
        if kind is None or kind.mime != 'application/pdf':
            detected = kind.mime if kind else 'desconocido'
            raise serializers.ValidationError(
                f"El archivo no es un PDF válido (tipo detectado: {detected}). "
                "Solo se permiten archivos PDF."
            )
        max_size = 50 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"El archivo es demasiado grande. Máximo: 50 MB. "
                f"Tu archivo: {value.size / (1024 * 1024):.2f} MB"
            )
        return value


class PlanSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Plan."""
    class Meta:
        """Metaclase de PlanSerializer."""
        model = Plan
        fields = '__all__'


class PagoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Pago."""
    usuario_email = serializers.CharField(source='oid_usuario.email', read_only=True)
    plan_nombre = serializers.CharField(source='oid_plan.nombre', read_only=True)

    class Meta:
        """Metaclase de PagoSerializer."""
        model = Pago
        fields = [
            'oid_pago', 'oid_usuario', 'usuario_email',
            'oid_plan', 'plan_nombre', 'monto',
            'fecha_pago', 'metodo_pago', 'estado_pago',
            'referencia_externa'
        ]
        read_only_fields = ['oid_pago', 'fecha_pago']


class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Notificacion."""
    class Meta:
        """Metaclase de NotificacionSerializer."""
        model = Notificacion
        fields = '__all__'
        read_only_fields = ['oid_notificacion', 'fecha_creacion']
