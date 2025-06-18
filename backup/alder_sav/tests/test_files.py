import unittest
from pathlib import Path
import tempfile
import shutil
import os
from alder_sav.utils.files import (
    save_file,
    read_file,
    delete_file,
    list_files,
    move_file,
    copy_file,
    get_file_info,
    validate_file_type,
    validate_file_size
)

class TestFileManager(unittest.TestCase):
    """Tests unitaires pour la gestion des fichiers."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.file_path = Path(self.temp_dir) / "test.txt"
        self.content = b"Ceci est un test."
        with open(self.file_path, "wb") as f:
            f.write(self.content)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_save_and_read_file(self):
        # Sauvegarde d'un fichier
        new_path = Path(self.temp_dir) / "save.txt"
        save_file(new_path, self.content)
        # Lecture du fichier
        data = read_file(new_path)
        self.assertEqual(data, self.content)

    def test_delete_file(self):
        delete_file(self.file_path)
        self.assertFalse(self.file_path.exists())

    def test_list_files(self):
        files = list_files(self.temp_dir)
        self.assertIn(str(self.file_path), files)

    def test_move_file(self):
        dest = Path(self.temp_dir) / "moved.txt"
        move_file(self.file_path, dest)
        self.assertTrue(dest.exists())
        self.assertFalse(self.file_path.exists())

    def test_copy_file(self):
        dest = Path(self.temp_dir) / "copy.txt"
        copy_file(self.file_path, dest)
        self.assertTrue(dest.exists())
        self.assertTrue(self.file_path.exists())

    def test_get_file_info(self):
        info = get_file_info(self.file_path)
        self.assertEqual(info["name"], "test.txt")
        self.assertEqual(info["size"], len(self.content))
        self.assertTrue("created_at" in info)

    def test_validate_file_type(self):
        self.assertTrue(validate_file_type(self.file_path, [".txt"]))
        self.assertFalse(validate_file_type(self.file_path, [".pdf"]))

    def test_validate_file_size(self):
        self.assertTrue(validate_file_size(self.file_path, max_size=100))
        self.assertFalse(validate_file_size(self.file_path, max_size=1))

if __name__ == '__main__':
    unittest.main() 