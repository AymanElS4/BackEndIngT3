from rest_framework import serializers
from ..models.pago import Pago

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
        read_only_fields = ['oid_pago', 'fecha_pago', 'oid_usuario']
