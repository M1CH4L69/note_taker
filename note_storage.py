import os
from datetime import datetime
from typing import List, Dict, Optional


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

    def get_notes_structured(self) -> List[Dict[str, object]]:
        """
        Return notes with parsed metadata for UI use.
        Each item: {index, datetime (or None), content, important}
        """
        blocks = self.read_notes_as_blocks()
        parsed: List[Dict[str, object]] = []

        for idx, block in enumerate(blocks):
            lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
            date_str: Optional[str] = None
            content = ""
            important = False

            for line in lines:
                if line.startswith("# Date:"):
                    date_str = line[len("# Date:"):].strip()
                elif line.startswith("# Note:"):
                    content = line[len("# Note:"):].strip()
                elif line.startswith("# Important:"):
                    important = line[len("# Important:"):].strip().lower() == "true"

            dt_val = None
            if date_str:
                try:
                    dt_val = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    dt_val = None

            parsed.append({
                "index": idx,
                "datetime": dt_val,
                "content": content,
                "important": important,
            })

        return parsed
