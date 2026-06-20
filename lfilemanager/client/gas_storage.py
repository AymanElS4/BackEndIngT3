import base64
import requests
from django.core.files.storage import Storage
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible

@deconstructible
class GASDriveStorage(Storage):
    def __init__(self, **kwargs):
        self.gas_url = kwargs.get('gas_url') or getattr(settings, 'GAS_WEBHOOK_URL', '')

    def _save(self, name, content):
        file_content = content.read()
        base64_file = base64.b64encode(file_content).decode('utf-8')
        
        payload = {
            "fileName": name.split('/')[-1],
            "fileType": getattr(content, 'content_type', 'application/pdf'),
            "base64File": base64_file
        }
        
        response = requests.post(self.gas_url, json=payload, allow_redirects=True)
        
        if response.status_code in [200, 301, 302]:
            try:
                data = response.json()
                if "error" in data:
                    raise Exception(f"GAS Error: {data['error']}")
                # Devolvemos el ID de Google Drive para guardarlo en la Base de Datos
                return data["id"]
            except Exception as e:
                raise Exception(f"Failed to parse GAS response: {response.text} | {str(e)}")
        else:
            raise Exception(f"Failed to upload to GAS, Status {response.status_code}")

    def url(self, name):
        # name será el ID del archivo
        return f"https://drive.google.com/uc?id={name}"

    def exists(self, name):
        # Siempre devolvemos False para que Django no intente buscar duplicados localmente
        return False
        
    def _open(self, name, mode='rb'):
        # Descargamos el archivo desde Google Drive a memoria RAM (ContentFile)
        # Esto previene problemas de CORS en el Frontend
        url = f"https://drive.google.com/uc?export=download&id={name}"
        resp = requests.get(url, allow_redirects=True)
        if resp.status_code == 200:
            return ContentFile(resp.content)
        else:
            raise FileNotFoundError(f"No se pudo descargar el archivo de Drive. Status: {resp.status_code}")
