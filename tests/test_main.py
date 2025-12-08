# python -m unittest tests/test_main.py
import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from note_storage import NoteStorage
from note_analyzer import NoteAnalyzer
from backup_manager import BackupManager


class TestNoteStorage(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_notes.txt")
        self.storage = NoteStorage(self.test_file)
    
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_read_notes_no_file(self):
        self.assertEqual(self.storage.read_notes_as_blocks(), [])
    
    def test_read_notes_parse_one(self):
        content = (
            "# Date: 2025-01-01\n# Note: Simple note\n# Important: False\n# ----------------------------------\n"
        )
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        notes = self.storage.read_notes_as_blocks()
        
        self.assertEqual(len(notes), 1)
        self.assertIn("Simple note", notes[0])
    
    def test_add_note(self):
        self.storage.add_note("Test note", important=False)
        notes = self.storage.read_notes_as_blocks()
        
        self.assertEqual(len(notes), 1)
        self.assertIn("Test note", notes[0])
    
    def test_add_empty_note_raises_error(self):
        with self.assertRaises(ValueError):
            self.storage.add_note("", important=False)
    
    def test_delete_note(self):
        self.storage.add_note("Note 1", important=False)
        self.storage.add_note("Note 2", important=True)
        
        self.assertEqual(self.storage.get_note_count(), 2)
        
        success = self.storage.delete_note(0)
        self.assertTrue(success)
        self.assertEqual(self.storage.get_note_count(), 1)
        
        notes = self.storage.read_notes_as_blocks()
        self.assertIn("Note 2", notes[0])
    
    def test_delete_invalid_index(self):
        self.storage.add_note("Test note", important=False)
        
        success = self.storage.delete_note(99)
        self.assertFalse(success)


class TestNoteAnalyzer(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.test_dir, "test_analysis.log")
        self.analyzer = NoteAnalyzer(self.log_file)
    
    def tearDown(self):
        if self.analyzer._running:
            self.analyzer.stop()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_analyzer_starts_and_stops(self):
        self.assertFalse(self.analyzer._running)
        self.analyzer.start()
        self.assertTrue(self.analyzer._running)
        self.analyzer.stop()
        self.assertFalse(self.analyzer._running)


class TestBackupManager(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.source_file = os.path.join(self.test_dir, "notes.txt")
        self.backup_file = os.path.join(self.test_dir, "notes.bak")
        self.backup_manager = BackupManager(
            self.source_file, 
            self.backup_file, 
            interval_seconds=1
        )
    
    def tearDown(self):
        if self.backup_manager._running:
            self.backup_manager.stop()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_backup_manager_starts_and_stops(self):
        self.assertFalse(self.backup_manager._running)
        self.backup_manager.start()
        self.assertTrue(self.backup_manager._running)
        self.backup_manager.stop()
        self.assertFalse(self.backup_manager._running)
    
    def test_create_backup_now(self):
        with open(self.source_file, "w") as f:
            f.write("test content")
        
        success = self.backup_manager.create_backup_now()
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.backup_file))
        
        with open(self.backup_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "test content")


if __name__ == "__main__":
    unittest.main()