"""Serializers for the Caso model — read and create/update views."""
from rest_framework import serializers
from ..models.caso import Caso
from ..models.documento import Documento
from .validators import validate_pdf_file


class CasoSerializer(serializers.ModelSerializer):
    """Serializer para Caso con datos expandidos."""
    abogado_nombre = serializers.CharField(
        source='oid_abogado.nombre', read_only=True)
    tipo_caso_nombre = serializers.CharField(
        source='oid_tipo_caso.nombre', read_only=True)
    estado_nombre = serializers.CharField(
        source='oid_estado.nombre', read_only=True)
    documentos_count = serializers.IntegerField(
        source='documentos.count', read_only=True)

    class Meta:
        """Metaclase de CasoSerializer."""
        model = Caso
        fields = [
            'oid_caso', 'oid_abogado', 'abogado_nombre',
            'oid_tipo_caso', 'tipo_caso_nombre',
            'oid_estado', 'estado_nombre',
            'titulo', 'descripcion', 'numero_expediente',
            'fecha_inicio', 'fecha_cierre', 'juzgado',
            'documentos_count'
        ]
        read_only_fields = ['oid_caso']


class CasoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear/editar un Caso con PDF."""
    archivo_pdf = serializers.FileField(
        required=False, allow_null=True, write_only=True)

    class Meta:
        """Metaclase de CasoCreateSerializer."""
        model = Caso
        fields = [
            'oid_abogado', 'oid_tipo_caso', 'oid_estado',
            'titulo', 'descripcion', 'numero_expediente',
            'fecha_inicio', 'fecha_cierre', 'juzgado', 'archivo_pdf'
        ]

    def validate_archivo_pdf(self, value):
        """Valida que el archivo adjunto sea un PDF válido 
        y no supere 50 MB."""
        return validate_pdf_file(value)

    def create(self, validated_data):
        """Crea el Caso descartando el archivo PDF
        , que se gestiona por separado."""
        validated_data.pop('archivo_pdf', None)
        caso = Caso.objects.create(**validated_data)
        return caso

    def update(self, instance, validated_data):
        """Actualiza el Caso y maneja la actualización del PDF asociado."""
        archivo_pdf = validated_data.pop('archivo_pdf', None)
        caso = super().update(instance, validated_data)
        if archivo_pdf:
            nombre_archivo = archivo_pdf.name.rsplit('.', 1)[0]
            Documento.objects.update_or_create(
                oid_caso=caso,
                tipo_documento='Documento Principal',
                defaults={
                    'nombre_archivo': nombre_archivo,
                    'ruta_archivo': archivo_pdf
                }
            )
        return caso
