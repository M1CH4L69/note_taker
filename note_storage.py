import os
from typing import List


class NoteStorage:
    
    def __init__(self, filename: str = "notes.txt"):
        self.filename = filename
    
    def add_note(self, content: str, important: bool = False) -> None:
        if not content.strip():
            raise ValueError("Cannot add empty note")
        
        import time
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        with open(self.filename, "a") as f:
            f.write(f"# Date: {timestamp}\n# Note: {content}\n# Important: {important}\n# ----------------------------------\n")
    
    def read_notes_as_blocks(self) -> List[str]:
        if not os.path.exists(self.filename):
            return []
        
        with open(self.filename, 'r') as file:
            content = file.read().strip()
        
        if not content:
            return []
        
        raw_notes = content.split("# ----------------------------------")
        notes = []
        for n in raw_notes:
            n = n.strip()
            if n:
                notes.append(n + "\n# ----------------------------------\n")
        
        return notes
    
    def delete_note(self, index: int) -> bool:
        notes = self.read_notes_as_blocks()
        
        if not (0 <= index < len(notes)):
            return False
        
        del notes[index]
        
        with open(self.filename, 'w') as file:
            for note in notes:
                file.write(note)
        
        return True
    
    def get_note_count(self) -> int:
        return len(self.read_notes_as_blocks())
