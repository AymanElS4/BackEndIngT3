"""Serializer for the Documento model."""
from rest_framework import serializers
from ..models.documento import Documento
from .validators import validate_pdf_file


class DocumentoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Documento."""
    class Meta:
        """Metaclase de DocumentoSerializer."""
        model = Documento
        fields = [
            'oid_documento', 'oid_caso', 'nombre_archivo',
            'ruta_archivo', 'tipo_documento', 'fecha_subida'
        ]
        read_only_fields = ['oid_documento', 'fecha_subida']

    def validate_ruta_archivo(self, value):
        """Valida que el archivo subido sea un PDF válido y no supere 50 MB."""
        return validate_pdf_file(value)
