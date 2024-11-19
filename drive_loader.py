from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import os


class DriveLoader:
    def __init__(self, credentials_path):
        # Verificar si el archivo de credenciales existe
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Credentials file not found at {credentials_path}")

        # Usar service_account.Credentials en lugar de Credentials
        self.creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/drive.readonly']  # Scope para lectura de Drive
        )

        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.posts_folder_id = '1r-kLg3B7QKY-5931rXlSPlsTK0RLaJQy'

    def download_markdown_files(self, destination_folder):
        """Descarga los archivos Markdown de una carpeta específica de Google Drive"""
        results = self.drive_service.files().list(
            q=f"'{self.posts_folder_id}' in parents and mimeType='text/markdown'",
            spaces='drive',
            fields="files(id, name)"
        ).execute()

        files = results.get('files', [])

        for file in files:
            file_id = file['id']
            file_name = file['name']

            request = self.drive_service.files().get_media(fileId=file_id)
            file_path = os.path.join(destination_folder, file_name)

            with open(file_path, 'wb') as file_handler:
                downloader = MediaIoBaseDownload(file_handler, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()