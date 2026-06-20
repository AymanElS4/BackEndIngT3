from rest_framework import serializers
from ..models.codigo_legal import CodigoLegal
from .validators import validate_pdf_file

class CodigoLegalListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados.

    Omite texto_contenido para no transferir cientos de KB por request.
    """
    estado_vigencia = serializers.SerializerMethodField()

    class Meta:
        """Metaclase de CodigoLegalListSerializer."""
        model = CodigoLegal
        fields = ['oid_codigo', 'nombre_norma', 'numero_articulo', 'vigencia', 'estado_vigencia', 'archivo_pdf']
        read_only_fields = ['oid_codigo']

    def get_estado_vigencia(self, obj):
        """Retorna la etiqueta de vigencia legible."""
        return 'Vigente' if obj.vigencia else 'Histórico'

class CodigoLegalSerializer(serializers.ModelSerializer):
    """Serializer completo para create/retrieve/update — incluye texto_contenido."""
    estado_vigencia = serializers.SerializerMethodField()
    archivo_pdf = serializers.FileField(required=False, allow_null=True)

    class Meta:
        """Metaclase de CodigoLegalSerializer."""
        model = CodigoLegal
        fields = [
            'oid_codigo', 'nombre_norma', 'numero_articulo',
            'texto_contenido', 'vigencia', 'estado_vigencia', 'archivo_pdf'
        ]
        read_only_fields = ['oid_codigo']

    def get_estado_vigencia(self, obj):
        """Retorna la etiqueta de vigencia legible."""
        return 'Vigente' if obj.vigencia else 'Histórico'

    def validate_archivo_pdf(self, value):
        """Valida que el archivo adjunto sea un PDF válido y no supere 50 MB."""
        return validate_pdf_file(value)
