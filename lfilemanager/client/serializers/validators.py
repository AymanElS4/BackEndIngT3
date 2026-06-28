"""Custom validators for DRF serializers — PDF file validation."""
import filetype
from rest_framework import serializers


def validate_pdf_file(value):
    """Valida que el archivo sea un PDF válido y no supere los 50 MB."""
    if value is None:
        return value

    header = value.read(261)
    value.seek(0)
    kind = filetype.guess(header)
    if kind is None or kind.mime != 'application/pdf':
        detected = kind.mime if kind else 'desconocido'
        raise serializers.ValidationError(
            f"El archivo no es un PDF válido (tipo detectado: {detected}). "
            "Solo se permiten archivos PDF."
        )

    max_size = 50 * 1024 * 1024
    if value.size > max_size:
        raise serializers.ValidationError(
            f"El archivo es demasiado grande. Máximo: 50 MB. "
            f"Tu archivo: {value.size / (1024 * 1024):.2f} MB"
        )
    return value
