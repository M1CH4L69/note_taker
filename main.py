import os
import time
import threading
import queue
import shutil

analysis_queue = queue.Queue()
print_lock = threading.Lock()

def clearscreen():
    os.system('cls' if os.name == 'nt' else 'clear')

def thread_safe_print(message):
    with print_lock:
        print(f"\n[BACKGROUND INFO]: {message}")

def note_analyzer_worker():
    while True:
        note_data = analysis_queue.get()
        if note_data is None:
            break
        content, is_important = note_data
        time.sleep(2)
        word_count = len(content.split())
        status = "URGENT" if is_important else "Normal"
        log_entry = f"Analyzed: '{content[:10]}...' | Words: {word_count} | Priority: {status}\n"
        with open("analysis_log.txt", "a") as log_file:
            log_file.write(log_entry)
        thread_safe_print(f"Note analyzed and saved to the log. (Word: {word_count})")
        analysis_queue.task_done()

def backup_scheduler(stop_event):
    while not stop_event.is_set():
        for _ in range(10):
            if stop_event.is_set():
                return
            time.sleep(1)
        if os.path.exists("notes.txt"):
            try:
                shutil.copy("notes.txt", "notes.bak")
            except Exception as e:
                thread_safe_print(f" Backup Error: {e}")

def addnote():
    note = input("Enter your note: ")
    if not note.strip():
        print("Empty note discarded.")
        return
    important_str = input("Is this note important? (y/n): ").lower().strip()
    important = important_str == 'y'
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open("notes.txt", "a") as f:
        f.write(f"# Date: {timestamp}\n# Note: {note}\n# Important: {important}\n# ----------------------------------\n")
    analysis_queue.put((note, important))
    print("Note added and sent for background analysis.")
    time.sleep(1)

def read_notes_as_blocks(filename='notes.txt'):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as file:
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

def deletenote():
    notes = read_notes_as_blocks()
    if not notes:
        print("No notes to delete.")
        input("Press Enter to return...")
        return
    for idx, note in enumerate(notes):
        print(f"--- Note {idx + 1} ---")
        print(note.strip())
        print()
    try:
        val = input("Enter the note number to delete (or 0 to cancel): ")
        if not val.isdigit():
            return
        index_to_delete = int(val) - 1
        if index_to_delete == -1:
            return
        if 0 <= index_to_delete < len(notes):
            del notes[index_to_delete]
            with open('notes.txt', 'w') as file:
                for note in notes:
                    file.write(note)
            print("Note deleted.")
        else:
            print("Invalid number.")
    except ValueError:
        print("Invalid input.")
    time.sleep(1)

def showmenu():
    print("1. Add Note (Triggers Background Analysis)")
    print("2. View Notes")
    print("3. Delete Note")
    print("4. Exit")

def user_input():
    analyzer_thread = threading.Thread(target=note_analyzer_worker, name="Analyzer-Thread", daemon=True)
    analyzer_thread.start()
    stop_backup_event = threading.Event()
    backup_thread = threading.Thread(target=backup_scheduler, args=(stop_backup_event,), name="Backup-Thread", daemon=True)
    backup_thread.start()
    print("System started. Background threads running")
    time.sleep(1)
    while True:
        showmenu()
        with print_lock:
            choice = input("Choose an option (1-4): ").strip()
        if choice == '1':
            clearscreen()
            addnote()
        elif choice == '2':
            clearscreen()
            notes = read_notes_as_blocks()
            if not notes:
                print("No notes found")
            for note in notes:
                print(note)
            input("\nPress Enter to return to menu")
            clearscreen()
        elif choice == '3':
            clearscreen()
            deletenote()
        elif choice == '4':
            print("Stopping background threads")
            stop_backup_event.set()
            analysis_queue.put(None)
            backup_thread.join()
            analyzer_thread.join()
            print("bye")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    user_input()