"""Serializer for the CasoNormativa join model (case ↔ legal code)."""
from rest_framework import serializers
from ..models.caso_normativa import CasoNormativa


class CasoNormativaSerializer(serializers.ModelSerializer):
    """Serializer para la relación entre Caso y CodigoLegal."""
    codigo_nombre = serializers.CharField(source='oid_codigo.nombre_norma', read_only=True)
    codigo_numero_articulo = serializers.CharField(source='oid_codigo.numero_articulo', read_only=True)
    codigo_vigencia = serializers.BooleanField(source='oid_codigo.vigencia', read_only=True)
    caso_titulo = serializers.CharField(source='oid_caso.titulo', read_only=True)

    class Meta:
        """Metaclase de CasoNormativaSerializer."""
        model = CasoNormativa
        fields = [
            'oid_relacion', 'oid_caso', 'caso_titulo',
            'oid_codigo', 'codigo_nombre', 'codigo_numero_articulo',
            'codigo_vigencia', 'fecha_asociacion'
        ]
        read_only_fields = ['oid_relacion', 'fecha_asociacion']

    def validate(self, attrs):
        """Evita duplicados con un mensaje claro (además del unique_together de la BD)."""
        caso = attrs.get('oid_caso')
        codigo = attrs.get('oid_codigo')
        if caso and codigo and CasoNormativa.objects.filter(
            oid_caso=caso, oid_codigo=codigo
        ).exists():
            raise serializers.ValidationError(
                'Este artículo ya está asociado a este caso.'
            )
        return attrs
