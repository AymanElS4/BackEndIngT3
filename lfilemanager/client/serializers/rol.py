from rest_framework import serializers
from ..models.rol import Rol

class RolSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Rol."""
    class Meta:
        """Metaclase de RolSerializer."""
        model = Rol
        fields = '__all__'
