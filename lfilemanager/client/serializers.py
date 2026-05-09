"""
Serializers para la API REST del sistema legal.
"""
from rest_framework import serializers
from .models import (
    Rol, Usuario, TipoCaso, EstadoCaso,
    Caso, CodigoLegal, CasoNormativa, Documento
)


# ============================================================
# Auth Serializers
# ============================================================

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de nuevos usuarios."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
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
        # Usar create_user para asegurar el hashing correcto de Django
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
        model = Usuario
        fields = [
            'nombre', 'email', 'oid_rol', 'estado',
            'matricula_profesional', 'especialidad', 'telefono_contacto'
        ]


# ============================================================
# Domain Serializers
# ============================================================

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'


class TipoCasoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoCaso
        fields = '__all__'


class EstadoCasoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoCaso
        fields = '__all__'


class CasoSerializer(serializers.ModelSerializer):
    """Serializer para Caso con datos expandidos."""
    abogado_nombre = serializers.CharField(source='oid_abogado.nombre', read_only=True)
    tipo_caso_nombre = serializers.CharField(source='oid_tipo_caso.nombre', read_only=True)
    estado_nombre = serializers.CharField(source='oid_estado.nombre', read_only=True)
    documentos_count = serializers.IntegerField(source='documentos.count', read_only=True)

    class Meta:
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
    """Serializer para crear/editar un Caso."""
    class Meta:
        model = Caso
        fields = [
            'oid_abogado', 'oid_tipo_caso', 'oid_estado',
            'titulo', 'descripcion', 'numero_expediente',
            'fecha_inicio', 'fecha_cierre', 'juzgado'
        ]


class CodigoLegalSerializer(serializers.ModelSerializer):
    estado_vigencia = serializers.SerializerMethodField()

    class Meta:
        model = CodigoLegal
        fields = [
            'oid_codigo', 'nombre_norma', 'numero_articulo',
            'texto_contenido', 'vigencia', 'estado_vigencia'
        ]
        read_only_fields = ['oid_codigo']

    def get_estado_vigencia(self, obj):
        return 'Vigente' if obj.vigencia else 'Histórico'


class CasoNormativaSerializer(serializers.ModelSerializer):
    codigo_nombre = serializers.CharField(source='oid_codigo.nombre_norma', read_only=True)
    caso_titulo = serializers.CharField(source='oid_caso.titulo', read_only=True)

    class Meta:
        model = CasoNormativa
        fields = [
            'oid_relacion', 'oid_caso', 'caso_titulo',
            'oid_codigo', 'codigo_nombre', 'fecha_asociacion'
        ]
        read_only_fields = ['oid_relacion', 'fecha_asociacion']


class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = [
            'oid_documento', 'oid_caso', 'nombre_archivo',
            'ruta_archivo', 'tipo_documento', 'fecha_subida'
        ]
        read_only_fields = ['oid_documento', 'fecha_subida']
