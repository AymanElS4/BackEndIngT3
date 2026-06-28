"""Serializer for the Notificacion model."""
from rest_framework import serializers
from ..models.notificacion import Notificacion


class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Notificacion."""
    class Meta:
        """Metaclase de NotificacionSerializer."""
        model = Notificacion
        fields = '__all__'
        read_only_fields = ['oid_notificacion', 'fecha_creacion']
        extra_kwargs = {
            'oid_usuario': {'required': False, 'allow_null': True}
        }
