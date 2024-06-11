import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from Startup.Global_Files import Developer_Gmail_Credential_File, Developer_Gmail_Token_File

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class DriveManager:
    def __init__(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(Developer_Gmail_Token_File):
            creds = Credentials.from_authorized_user_file(Developer_Gmail_Token_File, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    Developer_Gmail_Credential_File, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(Developer_Gmail_Token_File, 'w') as token:
                token.write(creds.to_json())

        try:
            self.drive_service = build('drive', 'v3', credentials=creds)
        except HttpError as error:
            print(f'An error occurred: {error}')

    def upload_file(self, file_path, file_name, folder_drive_id):
        file_metadata = {
            'name': file_name,
            'mimeType': '*/*',
            'parents': [folder_drive_id]
        }
        media = MediaFileUpload(fr"{file_path}",
                                mimetype='*/*',
                                resumable=True)
        file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

    def delete_file(self, file_id):
        file = self.drive_service.files().delete(fileId=file_id).execute()
        return file
