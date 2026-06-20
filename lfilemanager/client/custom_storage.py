from gdstorage.storage import GoogleDriveStorage
from django.conf import settings
import os

class CustomGoogleDriveStorage(GoogleDriveStorage):
    def _save(self, name, content):
        """
        Override _save to force the root folder to be the one specified in GOOGLE_DRIVE_STORAGE_MEDIA_ROOT
        """
        # The library uses settings.GOOGLE_DRIVE_STORAGE_MEDIA_ROOT as a string prefix by default.
        # We instead want to use it as the Google Drive Folder ID parent.
        import mimetypes
        from googleapiclient.http import MediaIoBaseUpload

        folder_id = getattr(settings, 'GOOGLE_DRIVE_STORAGE_MEDIA_ROOT', None)
        
        # If no folder_id is set, fallback to default behavior
        if not folder_id:
            return super()._save(name, content)

        # Create the subfolders if needed inside the parent_id
        folder_path = os.path.sep.join(self._split_path(name)[:-1])
        folder_data = self._get_or_create_folder(folder_path, parent_id=folder_id)
        
        parent_id = folder_data['id'] if folder_data else folder_id

        mime_type = mimetypes.guess_type(name)
        if mime_type[0] is None:
            mime_type = self._UNKNOWN_MIMETYPE_
            
        media_body = MediaIoBaseUpload(content.file, mime_type, resumable=True, chunksize=1024 * 512)
        body = {
            'name': self._split_path(name)[-1],
            'mimeType': mime_type,
            'parents': [parent_id]
        }
        
        file_data = self._drive_service.files().create(
            body=body,
            media_body=media_body
        ).execute()

        # Setting up permissions
        for p in self._permissions:
            self._drive_service.permissions().create(
                fileId=file_data["id"],
                body={**p.raw}
            ).execute()

        return file_data.get('originalFilename', file_data.get('name'))
