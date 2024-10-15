import os
import zipfile
import logging
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# 辅助函数

def find_file(service, folder_id, file_name):
    """在指定的 Google Drive 文件夹中查找文件"""
    query = f'name = "{file_name}" and "{folder_id}" in parents and trashed=false'
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType, size)'
    ).execute()
    items = results.get('files', [])
    if not items:
        logging.error('未找到文件 "%s"', file_name)
        return None
    return items[0]

def download_file(service, file_id, destination_path):
    """从 Google Drive 下载文件"""
    request = service.files().get_media(fileId=file_id)
    with open(destination_path, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                logging.info('下载进度：%d%%', progress)
    logging.info('下载完成，文件大小：%s bytes', os.path.getsize(destination_path))

def upload_file(service, folder_id, file_path, file_name):
    """将文件上传到 Google Drive"""
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaFileUpload(file_path, mimetype='application/zip')
    existing_file = find_file(service, folder_id, file_name)
    if existing_file:
        file_id = existing_file['id']
        logging.info('更新已有文件，文件ID：%s', file_id)
        service.files().update(fileId=file_id, media_body=media).execute()
    else:
        logging.info('上传新文件')
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    logging.info('文件 "%s" 已成功上传到 Google Drive', file_name)

def compress_folder(folder_path, zip_path, exclude_files=None):
    """压缩文件夹为 ZIP 文件"""
    logging.info('压缩文件夹 "%s"', folder_path)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for root, _, files in os.walk(folder_path):
            for file in files:
                if exclude_files and file in exclude_files:
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zip_ref.write(file_path, arcname)
    logging.info('压缩完成，ZIP 文件路径：%s', zip_path)

def extract_zip(zip_path, extract_to):
    """解压 ZIP 文件到指定目录"""
    logging.info('解压文件 "%s" 到 "%s"', zip_path, extract_to)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        bad_file = zip_ref.testzip()
        if bad_file:
            logging.error('ZIP 文件损坏：%s', bad_file)
            return False
        zip_ref.extractall(extract_to)
    logging.info('解压完成')
    return True

# 主函数

def download_save(service, folder_id, save_folder_name, save_path):
    logging.info('开始下载存档 "%s"', save_folder_name)
    try:
        file_name = f'{save_folder_name}.zip'
        file = find_file(service, folder_id, file_name)
        if not file:
            return
        mime_type = file.get('mimeType', '')
        if mime_type.startswith('application/vnd.google-apps'):
            logging.error('文件 "%s" 是 Google Apps 类型，无法直接下载', file_name)
            return

        zip_folder = os.path.join(save_path, 'saves')
        zip_path = os.path.join(zip_folder, file_name)
        os.makedirs(zip_folder, exist_ok=True)

        download_file(service, file['id'], zip_path)

        if extract_zip(zip_path, zip_folder):
            logging.info('存档 "%s" 下载并解压成功', save_folder_name)
        else:
            logging.error('解压存档 "%s" 失败', save_folder_name)
            return

        os.remove(zip_path)
        logging.info('删除临时文件 "%s"', zip_path)
    except Exception as e:
        logging.error('下载存档 "%s" 时出错：%s', save_folder_name, e)

def upload_save(service, folder_id, save_folder_name, save_path):
    logging.info('开始上传存档 "%s"', save_folder_name)
    try:
        save_folder_path = os.path.join(save_path, 'saves', save_folder_name)
        zip_path = os.path.join(save_path, 'saves', f'{save_folder_name}.zip')

        compress_folder(save_folder_path, zip_path)

        upload_file(service, folder_id, zip_path, f'{save_folder_name}.zip')

        os.remove(zip_path)
        logging.info('删除临时文件 "%s"', zip_path)
    except Exception as e:
        logging.error('上传存档 "%s" 时出错：%s', save_folder_name, e)

def download_mod(service, folder_id, save_path):
    logging.info('开始下载 MOD')
    try:
        file_name = 'mods.zip'
        file = find_file(service, folder_id, file_name)
        if not file:
            return
        mime_type = file.get('mimeType', '')
        if mime_type.startswith('application/vnd.google-apps'):
            logging.error('文件 "%s" 是 Google Apps 类型，无法直接下载', file_name)
            return

        mods_folder = os.path.join(save_path, 'mods')
        zip_path = os.path.join(mods_folder, file_name)
        os.makedirs(mods_folder, exist_ok=True)

        download_file(service, file['id'], zip_path)

        if extract_zip(zip_path, mods_folder):
            logging.info('MOD 下载并解压成功')
        else:
            logging.error('解压 MOD 失败')
            return

        os.remove(zip_path)
        logging.info('删除临时文件 "%s"', zip_path)
    except Exception as e:
        logging.error('下载 MOD 时出错：%s', e)

def upload_mod(service, folder_id, save_path):
    logging.info('开始上传 MOD')
    try:
        mods_folder = os.path.join(save_path, 'mods')
        zip_path = os.path.join(mods_folder, 'mods.zip')

        compress_folder(mods_folder, zip_path, exclude_files=['mods.zip'])

        upload_file(service, folder_id, zip_path, 'mods.zip')

        os.remove(zip_path)
        logging.info('删除临时文件 "%s"', zip_path)
    except Exception as e:
        logging.error('上传 MOD 时出错：%s', e)
