import calendar
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from note_storage import NoteStorage
from note_analyzer import NoteAnalyzer
from backup_manager import BackupManager


class CalendarGUI:
    def __init__(self):
        self.storage = NoteStorage()
        self.analyzer = NoteAnalyzer()
        self.backup = BackupManager()

        self.analyzer.start()
        self.backup.start()

        now = datetime.now()
        self.year = now.year
        self.month = now.month
        self.selected_day = now.day
        self.notes_cache = []
        self.day_index_map = []

        self.root = tk.Tk()
        self.root.title("Note Calendar (notes.txt)")
        self.root.geometry("960x640")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self._build_header()
        self._build_form()
        self._build_body()
        self.render_calendar()
        self.render_day_notes()

    def _build_header(self) -> None:
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, pady=8, padx=10)

        self.title_var = tk.StringVar()

        prev_btn = ttk.Button(header, text="<", command=self.prev_month)
        prev_btn.pack(side=tk.LEFT, padx=5)

        title_lbl = ttk.Label(header, textvariable=self.title_var, font=("Segoe UI", 14, "bold"))
        title_lbl.pack(side=tk.LEFT, padx=10)

        next_btn = ttk.Button(header, text=">", command=self.next_month)
        next_btn.pack(side=tk.LEFT, padx=5)

        reload_btn = ttk.Button(header, text="Reload", command=self.reload_notes)
        reload_btn.pack(side=tk.RIGHT, padx=5)

    def _build_form(self) -> None:
        form = ttk.Frame(self.root)
        form.pack(fill=tk.X, pady=6, padx=10)

        ttk.Label(form, text="Note:").grid(row=0, column=0, sticky="w")
        self.note_text = tk.Text(form, height=3, width=60)
        self.note_text.grid(row=0, column=1, columnspan=3, sticky="ew", padx=5)

        self.important_var = tk.BooleanVar(value=False)
        important_chk = ttk.Checkbutton(form, text="Important", variable=self.important_var)
        important_chk.grid(row=1, column=1, sticky="w", padx=5, pady=4)

        add_btn = ttk.Button(form, text="Add Note", command=self.add_note)
        add_btn.grid(row=1, column=2, sticky="w", padx=5, pady=4)

        self.status_var = tk.StringVar(value="")
        status_lbl = ttk.Label(form, textvariable=self.status_var, foreground="#0a5")
        status_lbl.grid(row=2, column=0, columnspan=4, sticky="w")

        for c in range(4):
            form.columnconfigure(c, weight=1)

    def _build_body(self) -> None:
        body = ttk.Frame(self.root)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        self.calendar_frame = ttk.Frame(body)
        self.calendar_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        right = ttk.Frame(body)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.day_label_var = tk.StringVar(value="Notes")
        day_lbl = ttk.Label(right, textvariable=self.day_label_var, font=("Segoe UI", 12, "bold"))
        day_lbl.pack(anchor="w")

        self.listbox = tk.Listbox(right, height=20)
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        delete_btn = ttk.Button(right, text="Delete selected note", command=self.delete_selected)
        delete_btn.pack(anchor="e")

    def reload_notes(self) -> None:
        self.render_calendar()
        self.render_day_notes()
        self.status_var.set("Reloaded from notes.txt")

    def add_note(self) -> None:
        content = self.note_text.get("1.0", tk.END).strip()
        if not content:
            self.status_var.set("Note cannot be empty.")
            return

        important = self.important_var.get()

        try:
            self.storage.add_note(content, important)
            self.analyzer.analyze_note(content, important)
        except ValueError as exc:
            self.status_var.set(str(exc))
            return

        self.status_var.set("Note saved to notes.txt")
        self.note_text.delete("1.0", tk.END)
        self.important_var.set(False)
        self.reload_notes()

    def delete_selected(self) -> None:
        selection = self.listbox.curselection()
        if not selection:
            self.status_var.set("Select a note to delete.")
            return

        idx_in_list = selection[0]
        if idx_in_list >= len(self.day_index_map):
            self.status_var.set("Selection out of range.")
            return

        note_index = self.day_index_map[idx_in_list]
        success = self.storage.delete_note(note_index)
        if success:
            self.status_var.set("Note deleted.")
            self.reload_notes()
        else:
            self.status_var.set("Could not delete note.")

    def render_calendar(self) -> None:
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.title_var.set(f"{calendar.month_name[self.month]} {self.year}")

        notes = self.storage.get_notes_structured()
        self.notes_cache = notes
        per_day = self._group_by_day(notes)

        for col, name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            lbl = ttk.Label(self.calendar_frame, text=name, anchor="center", padding=4)
            lbl.grid(row=0, column=col, sticky="nsew")

        first_weekday, num_days = calendar.monthrange(self.year, self.month)
        row = 1
        col = (first_weekday + 6) % 7

        for day in range(1, num_days + 1):
            frame = ttk.Frame(self.calendar_frame, borderwidth=1, relief="solid", padding=4)
            frame.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

            btn = ttk.Button(frame, text=str(day), command=lambda d=day: self.select_day(d))
            btn.pack(anchor="nw")

            for note in per_day.get(day, [])[:3]:
                preview = note.get("content", "")[:40]
                imp = " !" if note.get("important") else ""
                lbl = ttk.Label(frame, text=preview + imp, anchor="w", wraplength=140, justify=tk.LEFT)
                lbl.pack(anchor="w")

            col += 1
            if col > 6:
                col = 0
                row += 1

        for r in range(row + 1):
            self.calendar_frame.rowconfigure(r, weight=1)
        for c in range(7):
            self.calendar_frame.columnconfigure(c, weight=1)

    def select_day(self, day: int) -> None:
        self.selected_day = day
        self.render_day_notes()

    def render_day_notes(self) -> None:
        self.listbox.delete(0, tk.END)
        self.day_index_map = []

        notes = self.notes_cache or self.storage.get_notes_structured()
        filtered = []
        for note in notes:
            dt_val = note.get("datetime")
            if not dt_val:
                continue
            if dt_val.year == self.year and dt_val.month == self.month and dt_val.day == self.selected_day:
                filtered.append(note)

        self.day_label_var.set(f"Notes on {self.year}-{self.month:02d}-{self.selected_day:02d}")

        for note in filtered:
            dt_val = note.get("datetime")
            time_str = dt_val.strftime("%H:%M") if dt_val else "--:--"
            imp = " [! ]" if note.get("important") else ""
            text = f"{time_str}{imp} {note.get('content', '')}"
            self.listbox.insert(tk.END, text)
            self.day_index_map.append(note.get("index"))

        if not filtered:
            self.listbox.insert(tk.END, "No notes for this day.")

    def _group_by_day(self, notes):
        grouped = {}
        for note in notes:
            dt_val = note.get("datetime")
            if not dt_val:
                continue
            if dt_val.year == self.year and dt_val.month == self.month:
                grouped.setdefault(dt_val.day, []).append(note)
        return grouped

    def prev_month(self) -> None:
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.selected_day = 1
        self.render_calendar()
        self.render_day_notes()

    def next_month(self) -> None:
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.selected_day = 1
        self.render_calendar()
        self.render_day_notes()

    def on_close(self) -> None:
        self.analyzer.stop()
        self.backup.stop()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    CalendarGUI().run()
