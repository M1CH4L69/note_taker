# python -m unittest tests/test_main.py
import os
import unittest
import importlib
import main

TEST_FILE = "test_notes.txt"

class MyTests(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_FILE):
            try:
                os.remove(TEST_FILE)
            except Exception:
                pass
        
        if os.path.exists("analysis_log.txt"):
             try:
                os.remove("analysis_log.txt")
             except Exception:
                pass

        importlib.reload(main)

    def tearDown(self):
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)

    def test_read_notes_no_file(self):
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)
            
        self.assertEqual(main.read_notes_as_blocks(TEST_FILE), [])

    def test_read_notes_parse_one(self):
        content = (
            "# Date: 2025-01-01\n# Note: Simple note\n# Important: False\n# ----------------------------------\n"
        )
        with open(TEST_FILE, "w", encoding="utf-8") as f:
            f.write(content)
            
        notes = main.read_notes_as_blocks(TEST_FILE)
        
        self.assertEqual(len(notes), 1)
        self.assertIn("Simple note", notes[0])

if __name__ == "__main__":
    unittest.main()