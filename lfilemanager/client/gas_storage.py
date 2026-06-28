"""Google Apps Script (GAS) Drive Storage backend for Django file uploads."""
import base64
import requests
from django.core.files.storage import Storage
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible


@deconstructible
class GASDriveStorage(Storage):
    """Custom Django Storage that saves files to Google Drive via a GAS webhook."""

    def __init__(self, **kwargs):
        """Initialise storage with the GAS webhook URL from settings."""
        self.gas_url = kwargs.get('gas_url') or getattr(
            settings, 'GAS_WEBHOOK_URL', '')

    def _save(self, name, content):
        """Upload a file to Google Drive and return its Drive file ID."""
        file_content = content.read()
        base64_file = base64.b64encode(file_content).decode('utf-8')

        path_parts = name.split('/')
        folder_path = '/'.join(path_parts[:-1]) if len(path_parts) > 1 else ''

        payload = {
            "fileName": path_parts[-1],
            "folderPath": folder_path,
            "fileType": getattr(content, 'content_type', 'application/pdf'),
            "base64File": base64_file
        }

        response = requests.post(
            self.gas_url, json=payload, allow_redirects=True, timeout=30
        )

        if response.status_code in [200, 301, 302]:
            try:
                data = response.json()
                if "error" in data:
                    raise ValueError(f"GAS Error: {data['error']}")
                file_id = (
                    data.get("id")
                    or data.get("fileId")
                    or data.get("id_archivo")
                    or data.get("file_id")
                )

                if file_id:
                    return str(file_id)

                raise ValueError(
                    f"El JSON de GAS no trajo ninguna llave conocida de ID. "
                    f"Respuesta recibida: {data}"
                )

            except ValueError:
                raise
            except Exception as exc:
                raise RuntimeError(
                    f"Failed to parse GAS response: {response.text} | {str(exc)}"
                ) from exc
        else:
            raise RuntimeError(
                f"Failed to upload to GAS, Status {response.status_code}"
            )

    def url(self, name):
        """Return a public Google Drive URL for the given file ID."""
        return f"https://drive.google.com/uc?id={name}"

    def exists(self, name):
        """Always return False so Django never looks for local duplicates."""
        return False

    def _open(self, name, mode='rb'):  # pylint: disable=unused-argument
        """Download a file from Google Drive into memory and 
        return a ContentFile."""
        url = f"https://drive.google.com/uc?export=download&id={name}"
        resp = requests.get(url, allow_redirects=True, timeout=30)
        if resp.status_code == 200:
            return ContentFile(resp.content)
        raise FileNotFoundError(
            f"No se pudo descargar el archivo de Drive. Status: {resp.status_code}"
        )

    # ------------------------------------------------------------------ #
    # Abstract Storage methods – not needed for GAS-backed storage         #
    # ------------------------------------------------------------------ #

    def delete(self, name):
        """Deletion not supported for GAS Drive storage."""

    def listdir(self, path):
        """Directory listing not supported for GAS Drive storage."""

    def size(self, name):
        """File size query not supported for GAS Drive storage."""

    def path(self, name):
        """Local filesystem path not applicable for GAS Drive storage."""

    def get_accessed_time(self, name):
        """Access-time query not supported for GAS Drive storage."""

    def get_created_time(self, name):
        """Creation-time query not supported for GAS Drive storage."""

    def get_modified_time(self, name):
        """Modification-time query not supported for GAS Drive storage."""
