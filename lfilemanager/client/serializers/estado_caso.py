from rest_framework import serializers
from ..models.estado_caso import EstadoCaso

class EstadoCasoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo EstadoCaso."""
    class Meta:
        """Metaclase de EstadoCasoSerializer."""
        model = EstadoCaso
        fields = '__all__'
