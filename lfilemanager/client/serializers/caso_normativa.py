from rest_framework import serializers
from ..models.caso_normativa import CasoNormativa

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
