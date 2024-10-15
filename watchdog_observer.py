import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import subprocess

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, script_name):
        self.script_name = script_name
        self.process = None
        self.restart_script()

    def restart_script(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen([sys.executable, self.script_name])

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"Detected changes in {event.src_path}. Restarting script...")
            self.restart_script()

def start_watching(script_name):
    path = os.path.dirname(os.path.abspath(script_name))
    event_handler = ChangeHandler(script_name)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watching("main.py")
