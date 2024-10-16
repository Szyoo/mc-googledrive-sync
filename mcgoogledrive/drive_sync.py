import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import logging

CONFIG_FILE = 'config/config.json'
TOKEN_FILE = 'config/token.pickle'
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_NAME = 'MC_GoogleDriveSync'

class GoogleDriveSync:
    def __init__(self):
        self.service = None
        self.folder_id = None

    def bind_google_drive(self):
        logging.info('开始绑定 Google Drive')
        try:
            creds = None
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'rb') as token:
                    creds = pickle.load(token)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file('config/credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
            self.service = build('drive', 'v3', credentials=creds)
            self.create_app_folder()
            logging.info('Google Drive 绑定成功')
        except Exception as e:
            logging.error('绑定 Google Drive 时出错: %s', e)
            raise

    def create_app_folder(self):
        logging.info('创建专属 Google Drive 文件夹')
        try:
            results = self.service.files().list(q=f'name = "{FOLDER_NAME}" and mimeType = "application/vnd.google-apps.folder" and trashed=false', spaces='drive').execute()
            items = results.get('files', [])
            if not items:
                file_metadata = {
                    'name': FOLDER_NAME,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.service.files().create(body=file_metadata, fields='id').execute()
                self.folder_id = folder.get('id')
                logging.info('创建文件夹成功，文件夹 ID: %s', self.folder_id)
            else:
                self.folder_id = items[0]['id']
                logging.info('文件夹已存在，文件夹 ID: %s', self.folder_id)
        except Exception as e:
            logging.error('创建专属文件夹时出错: %s', e)
            raise

    def list_files(self):
        logging.info('列出专属文件夹中的文件')
        try:
            if not self.folder_id:
                raise ValueError('未找到专属文件夹 ID')
            results = self.service.files().list(
                q=f'"{self.folder_id}" in parents and trashed=false', 
                spaces='drive', 
                fields='files(id, name, modifiedTime, size)'
            ).execute()
            items = results.get('files', [])
            return items
        except Exception as e:
            logging.error('列出文件时出错: %s', e)
            raise
