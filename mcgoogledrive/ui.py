import os
import tkinter as tk
from tkinter import filedialog, scrolledtext
import threading
import logging
from datetime import datetime, timezone
from mcgoogledrive.drive_sync import TOKEN_FILE, GoogleDriveSync
from mcgoogledrive.config import load_config, save_config
from mcgoogledrive.utils import setup_logging
from mcgoogledrive.file_operations import download_save, upload_save, download_mod, upload_mod

class GoogleDriveSyncApp:
    def __init__(self, root):
        setup_logging()  # 设置日志
        logging.info('初始化 GoogleDriveSyncApp')
        self.root = root
        self.root.title('Google Drive Sync Tool')
        self.drive_sync = GoogleDriveSync()
        self.config = load_config()

        # UI Elements
        self.setup_ui()
        self.root.update()

        # 自动绑定 Google Drive（如果存在凭据）
        self.auto_bind_google_drive_thread()

    def setup_ui(self):
        logging.info('设置 UI 元素')
        self.root.geometry('600x600')
        self.root.configure(padx=20, pady=20)

        # 设置最小宽度
        self.root.minsize(600, 600)

        # Google Drive 绑定按钮
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill='x', pady=5)
        self.button_frame.columnconfigure(3, weight=1)
        self.bind_drive_label = tk.Label(self.button_frame, text='Google Drive 绑定', anchor='w', width=15)
        self.bind_drive_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.bind_drive_button = tk.Button(self.button_frame, text='绑定 Google Drive', command=self.bind_google_drive_thread)
        self.bind_drive_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.rebind_drive_button = tk.Button(self.button_frame, text='重新绑定', command=self.rebind_google_drive_thread, state=tk.DISABLED)
        self.rebind_drive_button.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        self.test_bind_button = tk.Button(self.button_frame, text='测试绑定', command=self.test_bind, state=tk.DISABLED)
        self.test_bind_button.grid(row=0, column=3, padx=5, pady=5, sticky='ew')

        # 存档路径输入框
        self.path_frame = tk.Frame(self.root)
        self.path_frame.pack(fill='x', pady=5)
        self.path_frame.columnconfigure(1, weight=1)
        self.path_label = tk.Label(self.path_frame, text='游戏文件夹', width=15, anchor='w')
        self.path_label.grid(row=0, column=0, padx=5, pady=5)
        self.path_entry = tk.Entry(self.path_frame)
        self.path_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        # 回填存档路径
        self.path_entry.insert(0, self.config.get('save_path', ''))
        self.path_button = tk.Button(self.path_frame, text='选择路径', command=self.select_path)
        self.path_button.grid(row=0, column=2, padx=5, pady=5)

        # 存档文件夹名字输入框
        self.folder_frame = tk.Frame(self.root)
        self.folder_frame.pack(fill='x', pady=5)
        self.folder_frame.columnconfigure(1, weight=1)
        self.folder_label = tk.Label(self.folder_frame, text='存档文件夹名字', width=15, anchor='w')
        self.folder_label.grid(row=0, column=0, padx=5, pady=5)
        self.folder_entry = tk.Entry(self.folder_frame)
        self.folder_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.folder_entry.insert(0, self.config.get('save_folder', ''))

        # 存档版本比较结果显示
        self.saves_version_frame = tk.Frame(self.root)
        self.saves_version_frame.pack(fill='x', pady=2)
        self.saves_version_frame.columnconfigure([1, 2], weight=1)

        self.drive_saves_label = tk.Label(self.saves_version_frame, text='Google Drive 存档', anchor='w', width=15)
        self.drive_saves_label.grid(row=0, column=0, padx=5, pady=2)
        self.drive_saves_time = tk.Label(self.saves_version_frame, text='', anchor='w')
        self.drive_saves_time.grid(row=0, column=1, padx=5, pady=2, sticky='w')
        self.drive_saves_size = tk.Label(self.saves_version_frame, text='', anchor='w')
        self.drive_saves_size.grid(row=0, column=2, padx=5, pady=2, sticky='w')

        self.local_saves_label = tk.Label(self.saves_version_frame, text='本地存档', anchor='w', width=15)
        self.local_saves_label.grid(row=1, column=0, padx=5, pady=2)
        self.local_saves_time = tk.Label(self.saves_version_frame, text='', anchor='w')
        self.local_saves_time.grid(row=1, column=1, padx=5, pady=2, sticky='w')
        self.local_saves_size = tk.Label(self.saves_version_frame, text='', anchor='w')
        self.local_saves_size.grid(row=1, column=2, padx=5, pady=2, sticky='w')

        # 下载/上传存档按钮
        self.save_buttons_frame = tk.Frame(self.root)
        self.save_buttons_frame.pack(fill='x', pady=5)
        self.save_buttons_frame.columnconfigure(1, weight=1)
        self.save_buttons_label = tk.Label(self.save_buttons_frame, text='存档管理', anchor='w', width=15)
        self.save_buttons_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.save_buttons_sub_frame = tk.Frame(self.save_buttons_frame)
        self.save_buttons_sub_frame.grid(row=0, column=1, sticky='ew')
        self.save_buttons_sub_frame.columnconfigure([0, 1], weight=1)
        self.download_save_button = tk.Button(self.save_buttons_sub_frame, text='下载存档', command=self.download_save_thread)
        self.download_save_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.upload_save_button = tk.Button(self.save_buttons_sub_frame, text='上传存档', command=self.upload_save_thread)
        self.upload_save_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # MOD 版本比较结果显示
        self.mods_version_frame = tk.Frame(self.root)
        self.mods_version_frame.pack(fill='x', pady=2)
        self.mods_version_frame.columnconfigure([1, 2], weight=1)

        self.drive_mods_label = tk.Label(self.mods_version_frame, text='Google Drive MOD', anchor='w', width=15)
        self.drive_mods_label.grid(row=0, column=0, padx=5, pady=2)
        self.drive_mods_time = tk.Label(self.mods_version_frame, text='', anchor='w')
        self.drive_mods_time.grid(row=0, column=1, padx=5, pady=2, sticky='w')
        self.drive_mods_size = tk.Label(self.mods_version_frame, text='', anchor='w')
        self.drive_mods_size.grid(row=0, column=2, padx=5, pady=2, sticky='w')

        self.local_mods_label = tk.Label(self.mods_version_frame, text='本地 MOD', anchor='w', width=15)
        self.local_mods_label.grid(row=1, column=0, padx=5, pady=2)
        self.local_mods_time = tk.Label(self.mods_version_frame, text='', anchor='w')
        self.local_mods_time.grid(row=1, column=1, padx=5, pady=2, sticky='w')
        self.local_mods_size = tk.Label(self.mods_version_frame, text='', anchor='w')
        self.local_mods_size.grid(row=1, column=2, padx=5, pady=2, sticky='w')

        # 下载/上传 MOD 按钮
        self.mod_buttons_frame = tk.Frame(self.root)
        self.mod_buttons_frame.pack(fill='x', pady=5)
        self.mod_buttons_frame.columnconfigure(1, weight=1)
        self.mod_buttons_label = tk.Label(self.mod_buttons_frame, text='MOD 管理', anchor='w', width=15)
        self.mod_buttons_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.mod_buttons_sub_frame = tk.Frame(self.mod_buttons_frame)
        self.mod_buttons_sub_frame.grid(row=0, column=1, sticky='ew')
        self.mod_buttons_sub_frame.columnconfigure([0, 1], weight=1)
        self.download_mod_button = tk.Button(self.mod_buttons_sub_frame, text='下载 MOD', command=self.download_mod_thread)
        self.download_mod_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.upload_mod_button = tk.Button(self.mod_buttons_sub_frame, text='上传 MOD', command=self.upload_mod_thread)
        self.upload_mod_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # 保存配置按钮
        self.save_config_frame = tk.Frame(self.root)
        self.save_config_frame.pack(fill='x', pady=10)
        self.save_config_frame.columnconfigure(1, weight=1)
        self.save_config_label = tk.Label(self.save_config_frame, text='保存配置', anchor='w', width=15)
        self.save_config_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.save_config_sub_frame = tk.Frame(self.save_config_frame)
        self.save_config_sub_frame.grid(row=0, column=1, sticky='ew')
        self.save_config_sub_frame.columnconfigure([0, 1], weight=1)
        self.save_config_button = tk.Button(self.save_config_sub_frame, text='保存配置', command=self.save_config)
        self.save_config_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.version_compare_button = tk.Button(self.save_config_sub_frame, text='版本比较', command=self.version_compare_thread)
        self.version_compare_button.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # 日志显示框
        self.log_frame = tk.Frame(self.root)
        self.log_frame.pack(fill='both', expand=True, pady=10)
        self.log_text = scrolledtext.ScrolledText(self.log_frame, state='disabled', height=10, wrap='word', bg='black', fg='white', font=('Courier', 10))
        self.log_text.pack(fill='both', expand=True)

        # 配置日志处理器来实时更新日志框
        self.setup_logging_handler()

        # 更新按钮状态
        self.update_buttons_state()

    def setup_logging_handler(self):
        handler = LoggingHandler(self.log_text)
        logging.getLogger().addHandler(handler)

    def select_path(self):
        logging.info('选择游戏文件夹路径')
        path = filedialog.askdirectory(mustexist=True, title='选择游戏文件夹路径（包含 assets, versions, saves, mods 等子文件夹）')
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def bind_google_drive_thread(self):
        logging.info('启动绑定 Google Drive 线程')
        threading.Thread(target=self.bind_google_drive, daemon=True).start()

    def bind_google_drive(self):
        try:
            self.drive_sync.bind_google_drive()
            logging.info('Google Drive 绑定成功')
            self.update_bind_button()
        except Exception as e:
            logging.error(f'绑定 Google Drive 时出错: {e}')

    def rebind_google_drive_thread(self):
        logging.info('启动重新绑定 Google Drive 线程')
        threading.Thread(target=self.rebind_google_drive, daemon=True).start()

    def rebind_google_drive(self):
        logging.info('重新绑定 Google Drive')
        try:
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
            self.bind_google_drive()
        except Exception as e:
            logging.error(f'重新绑定 Google Drive 时出错: {e}')

    def auto_bind_google_drive_thread(self):
        logging.info('启动自动绑定 Google Drive 线程')
        threading.Thread(target=self.auto_bind_google_drive, daemon=True).start()

    def auto_bind_google_drive(self):
        logging.info('尝试自动绑定 Google Drive')
        try:
            if os.path.exists(TOKEN_FILE):
                self.drive_sync.bind_google_drive()
                self.update_bind_button()
                if self.check_config_validity():
                    self.version_compare_thread()
            else:
                logging.info('未找到本地凭据，跳过自动绑定')
        except Exception as e:
            logging.error(f'自动绑定 Google Drive 时出错: {e}')

    def update_bind_button(self):
        self.bind_drive_button.config(text='Google Drive 已绑定', state=tk.DISABLED)
        self.rebind_drive_button.config(state=tk.NORMAL)
        self.test_bind_button.config(state=tk.NORMAL)

    def check_config_validity(self):
        if not self.config.get('save_path') or not self.config.get('save_folder'):
            return False
        return True

    def update_buttons_state(self):
        is_valid = self.check_config_validity()
        state = tk.NORMAL if is_valid else tk.DISABLED
        self.download_save_button.config(state=state)
        self.upload_save_button.config(state=state)
        self.download_mod_button.config(state=state)
        self.upload_mod_button.config(state=state)
        self.version_compare_button.config(state=state)

    def save_config(self):
        logging.info('保存配置')
        self.config['save_path'] = self.path_entry.get()
        self.config['save_folder'] = self.folder_entry.get()
        save_config(self.config)
        logging.info('配置已保存')
        self.update_buttons_state()

    def download_save_thread(self):
        logging.info('启动下载存档线程')
        threading.Thread(target=lambda: download_save(
            self.drive_sync.service,
            self.drive_sync.folder_id,
            self.folder_entry.get(),
            self.path_entry.get()
        ), daemon=True).start()

    def upload_save_thread(self):
        logging.info('启动上传存档线程')
        threading.Thread(target=lambda: upload_save(
            self.drive_sync.service,
            self.drive_sync.folder_id,
            self.folder_entry.get(),
            self.path_entry.get()
        ), daemon=True).start()

    def download_mod_thread(self):
        logging.info('启动下载 MOD 线程')
        threading.Thread(target=lambda: download_mod(
            self.drive_sync.service,
            self.drive_sync.folder_id,
            self.path_entry.get()
        ), daemon=True).start()

    def upload_mod_thread(self):
        logging.info('启动上传 MOD 线程')
        threading.Thread(target=lambda: upload_mod(
            self.drive_sync.service,
            self.drive_sync.folder_id,
            self.path_entry.get()
        ), daemon=True).start()

    def test_bind(self):
        logging.info('测试绑定，获取文件列表')
        try:
            files = self.drive_sync.list_files()
            logging.info(f'绑定文件夹内共有 {len(files)} 个文件：')
            for file in files:
                logging.info(f'- {file["name"]}')
        except Exception as e:
            logging.error(f'测试绑定时出错: {e}')

    def version_compare_thread(self):
        logging.info('启动版本比较线程')
        threading.Thread(target=self.version_compare, daemon=True).start()

    def version_compare(self):
        logging.info('开始版本比较')
        try:
            # 定义需要查找的文件名
            save_zip_name = f"{self.folder_entry.get()}.zip"
            mods_zip_name = "mods.zip"

            # 通过文件名查找存档ZIP文件
            save_query = f'name = "{save_zip_name}" and "{self.drive_sync.folder_id}" in parents and trashed=false'
            save_results = self.drive_sync.service.files().list(
                q=save_query,
                spaces='drive',
                fields='files(id, name, modifiedTime, size)'
            ).execute()
            save_items = save_results.get('files', [])
            if not save_items:
                logging.error(f'未找到名为 "{save_zip_name}" 的存档文件')
                return
            drive_saves_file = save_items[0]

            # 通过文件名查找MOD ZIP文件
            mods_query = f'name = "{mods_zip_name}" and "{self.drive_sync.folder_id}" in parents and trashed=false'
            mods_results = self.drive_sync.service.files().list(
                q=mods_query,
                spaces='drive',
                fields='files(id, name, modifiedTime, size)'
            ).execute()
            mods_items = mods_results.get('files', [])
            if not mods_items:
                logging.error(f'未找到名为 "{mods_zip_name}" 的MOD文件')
                return
            drive_mods_file = mods_items[0]

            # 转换 Google Drive 的时间格式为本地可读格式
            drive_saves_time_utc = datetime.strptime(drive_saves_file["modifiedTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
            drive_mods_time_utc = datetime.strptime(drive_mods_file["modifiedTime"], "%Y-%m-%dT%H:%M:%S.%fZ")

            # 转换为本地时间
            drive_saves_time = drive_saves_time_utc.replace(tzinfo=timezone.utc).astimezone()
            drive_mods_time = drive_mods_time_utc.replace(tzinfo=timezone.utc).astimezone()

            # 更新 UI 中的 Google Drive 存档信息
            self.drive_saves_time.config(text=f'修改时间: {drive_saves_time.strftime("%Y-%m-%d %H:%M:%S")}')
            self.drive_saves_size.config(text=f'大小: {drive_saves_file.get("size")} bytes')

            # 更新 UI 中的 Google Drive MOD 信息
            self.drive_mods_time.config(text=f'修改时间: {drive_mods_time.strftime("%Y-%m-%d %H:%M:%S")}')
            self.drive_mods_size.config(text=f'大小: {drive_mods_file.get("size")} bytes')

            # 获取本地存档和 MOD 文件的路径
            local_saves_path = os.path.join(self.path_entry.get(), 'saves', self.folder_entry.get())
            local_mods_path = os.path.join(self.path_entry.get(), 'mods')

            # 检查本地存档和 MOD 文件夹是否存在
            if not os.path.exists(local_saves_path):
                logging.error(f'本地存档路径不存在: {local_saves_path}')
                return
            if not os.path.exists(local_mods_path):
                logging.error(f'本地 MOD 路径不存在: {local_mods_path}')
                return

            # 获取本地存档文件夹内所有文件的最新修改时间
            local_saves_time = self.get_latest_modified_time(local_saves_path)
            local_mods_time = datetime.fromtimestamp(os.path.getmtime(local_mods_path))

            # 获取文件夹大小
            local_saves_size = self.get_folder_size(local_saves_path)
            local_mods_size = self.get_folder_size(local_mods_path)

            # 更新 UI 中的本地存档信息
            self.local_saves_time.config(text=f'修改时间: {local_saves_time.strftime("%Y-%m-%d %H:%M:%S")}')
            self.local_saves_size.config(text=f'大小: {local_saves_size} bytes')

            # 更新 UI 中的本地 MOD 信息
            self.local_mods_time.config(text=f'修改时间: {local_mods_time.strftime("%Y-%m-%d %H:%M:%S")}')
            self.local_mods_size.config(text=f'大小: {local_mods_size} bytes')

            logging.info('版本比较成功，已刷新数据显示')

        except Exception as e:
            logging.error(f'版本比较时出错: {e}')

    # 辅助方法：获取文件夹内最新文件的修改时间
    def get_latest_modified_time(self, folder_path):
        latest_time = None
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_time = os.path.getmtime(file_path)
                if latest_time is None or file_time > latest_time:
                    latest_time = file_time
        return datetime.fromtimestamp(latest_time) if latest_time else None

    def get_folder_size(self, folder_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

class LoggingHandler(logging.Handler):
    def __init__(self, log_widget):
        super().__init__()
        self.log_widget = log_widget

    def emit(self, record):
        msg = self.format(record)
        self.log_widget.configure(state='normal')
        self.log_widget.insert(tk.END, f'{msg}\n')
        self.log_widget.configure(state='disabled')
        self.log_widget.yview(tk.END)

if __name__ == '__main__':
    logging.info('启动应用程序')
    root = tk.Tk()
    app = GoogleDriveSyncApp(root)
    root.mainloop()
