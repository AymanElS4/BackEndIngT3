from rest_framework import serializers
from ..models.tipo_caso import TipoCaso

class TipoCasoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo TipoCaso."""
    class Meta:
        """Metaclase de TipoCasoSerializer."""
        model = TipoCaso
        fields = '__all__'
