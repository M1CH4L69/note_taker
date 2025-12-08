import queue
import threading
import time

class NoteAnalyzer:
    
    def __init__(self, log_file: str = "analysis_log.txt"):
        self.log_file = log_file
        self.analysis_queue: queue.Queue = queue.Queue()
        self.print_lock = threading.Lock()
        self._thread: threading.Thread = None
        self._running = False
    
    def start(self) -> None:
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(
            target=self._worker,
            name="Analyzer-Thread",
            daemon=True
        )
        self._thread.start()
    
    def stop(self) -> None:
        if not self._running:
            return
        
        self._running = False
        self.analysis_queue.put(None)
        if self._thread:
            self._thread.join()
    
    def analyze_note(self, content: str, is_important: bool) -> None:
        self.analysis_queue.put((content, is_important))
    
    def _worker(self) -> None:
        while True:
            note_data = self.analysis_queue.get()
            if note_data is None:
                break
            
            content, is_important = note_data
            time.sleep(2)
            
            word_count = len(content.split())
            status = "URGENT" if is_important else "Normal"
            log_entry = f"Analyzed: '{content[:10]}...' | Words: {word_count} | Priority: {status}\n"
            
            with open(self.log_file, "a") as log_file:
                log_file.write(log_entry)
            
            self._thread_safe_print(f"Note analyzed and saved to the log. (Words: {word_count})")
            self.analysis_queue.task_done()
    
    def _thread_safe_print(self, message: str) -> None:
        with self.print_lock:
            print(f"\n[BACKGROUND INFO]: {message}")
