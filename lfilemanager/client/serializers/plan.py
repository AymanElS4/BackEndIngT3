from rest_framework import serializers
from ..models.plan import Plan

class PlanSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Plan."""
    class Meta:
        """Metaclase de PlanSerializer."""
        model = Plan
        fields = '__all__'
