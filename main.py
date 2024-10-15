import logging
import tkinter as tk
from mcgoogledrive.ui import GoogleDriveSyncApp

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info('启动应用程序')
    root = tk.Tk()
    app = GoogleDriveSyncApp(root)
    root.mainloop()
