from rest_framework import serializers
from ..models.rol import Rol
from ..models.usuario import Usuario

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
