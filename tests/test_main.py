import os
import unittest
import importlib

import main


class MyTests(unittest.TestCase):
    def setUp(self):
        for fname in ("notes.txt", "analysis_log.txt"):
            try:
                os.remove(fname)
            except Exception:
                pass
        importlib.reload(main)

    def test_read_notes_no_file(self):
        # When no notes file exists, function returns empty list
        if os.path.exists("notes.txt"):
            os.remove("notes.txt")
        self.assertEqual(main.read_notes_as_blocks(), [])

    def test_read_notes_parse_one(self):
        # Basic parsing of a single note block
        content = (
            "# Date: 2025-01-01\n# Note: Simple note\n# Important: False\n# ----------------------------------\n"
        )
        with open("notes.txt", "w", encoding="utf-8") as f:
            f.write(content)
        notes = main.read_notes_as_blocks()
        self.assertEqual(len(notes), 1)
        self.assertIn("Simple note", notes[0])

if __name__ == "__main__":
    unittest.main()
