import os
import time
from note_storage import NoteStorage
from note_analyzer import NoteAnalyzer
from backup_manager import BackupManager


class NoteTakerUI:
    
    def __init__(self):
        self.storage = NoteStorage()
        self.analyzer = NoteAnalyzer()
        self.backup_manager = BackupManager()
        self.print_lock = None
    
    def start(self) -> None:
        self.analyzer.start()
        self.backup_manager.start()
        print("System started. Background threads running")
        time.sleep(1)
    
    def stop(self) -> None:
        print("Stopping background threads...")
        self.backup_manager.stop()
        self.analyzer.stop()
        print("Goodbye!")
    
    def clear_screen(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_menu(self) -> None:
        print("\n" + "="*50)
        print("NOTE TAKER APPLICATION")
        print("="*50)
        print("1. Add Note (Triggers Background Analysis)")
        print("2. View Notes")
        print("3. Delete Note")
        print("4. Exit")
        print("="*50)
    
    def add_note_interactive(self) -> None:
        try:
            note = input("Enter your note: ").strip()
            if not note:
                print("Empty note discarded.")
                return
            
            important_str = input("Is this note important? (y/n): ").lower().strip()
            important = important_str == 'y'
            
            self.storage.add_note(note, important)
            self.analyzer.analyze_note(note, important)
            print("Note added and sent for background analysis.")
            time.sleep(1)
        except ValueError as e:
            print(f"Error: {e}")
    
    def view_notes_interactive(self) -> None:
        notes = self.storage.read_notes_as_blocks()
        
        if not notes:
            print("No notes found.")
        else:
            for idx, note in enumerate(notes, 1):
                print(f"\n--- Note {idx} ---")
                print(note)
        
        input("\nPress Enter to return to menu...")
    
    def delete_note_interactive(self) -> None:
        notes = self.storage.read_notes_as_blocks()
        
        if not notes:
            print("No notes to delete.")
            input("Press Enter to return...")
            return
        
        print("\nAvailable notes:\n")
        for idx, note in enumerate(notes, 1):
            print(f"--- Note {idx} ---")
            print(note.strip())
            print()
        
        try:
            val = input("Enter the note number to delete (or 0 to cancel): ").strip()
            
            if not val.isdigit():
                print("Invalid input.")
                return
            
            note_number = int(val)
            
            if note_number == 0:
                return
            
            index_to_delete = note_number - 1
            
            if self.storage.delete_note(index_to_delete):
                print("Note deleted successfully.")
            else:
                print("Invalid note number.")
        except ValueError:
            print("Invalid input.")
        
        time.sleep(1)
    
    def run(self) -> None:
        self.start()
        
        try:
            while True:
                self.show_menu()
                choice = input("Choose an option (1-4): ").strip()
                
                if choice == '1':
                    self.clear_screen()
                    self.add_note_interactive()
                elif choice == '2':
                    self.clear_screen()
                    self.view_notes_interactive()
                    self.clear_screen()
                elif choice == '3':
                    self.clear_screen()
                    self.delete_note_interactive()
                    self.clear_screen()
                elif choice == '4':
                    break
                else:
                    print("Invalid choice. Please try again.")
        except KeyboardInterrupt:
            print("\nApplication interrupted by user.")
        finally:
            self.stop()
