import os
import shutil
import threading
import time


class BackupManager:
    
    def __init__(self, source_file: str = "notes.txt", backup_file: str = "notes.bak", interval_seconds: int = 10):
        self.source_file = source_file
        self.backup_file = backup_file
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread: threading.Thread = None
        self._running = False
    
    def start(self) -> None:
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._backup_worker,
            name="Backup-Thread",
            daemon=True
        )
        self._thread.start()
    
    def stop(self) -> None:
        if not self._running:
            return
        
        self._running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join()
    
    def _backup_worker(self) -> None:
        while not self._stop_event.is_set():
            for _ in range(self.interval_seconds):
                if self._stop_event.is_set():
                    return
                time.sleep(1)
            
            if os.path.exists(self.source_file):
                try:
                    shutil.copy(self.source_file, self.backup_file)
                except Exception as e:
                    print(f"\n[BACKUP ERROR]: {e}")
    
    def create_backup_now(self) -> bool:
        if not os.path.exists(self.source_file):
            return False
        
        try:
            shutil.copy(self.source_file, self.backup_file)
            return True
        except Exception as e:
            print(f"\n[BACKUP ERROR]: {e}")
            return False
