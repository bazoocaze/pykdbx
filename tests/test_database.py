from unittest import TestCase

import fixtures
from src.database import KeyValue, Folder, File


class TestDatabase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        fixtures.remove_all()
        fixtures.create_test_database()

    @classmethod
    def tearDownClass(cls) -> None:
        fixtures.remove_all()

    def test_db_with_one_entry(self):
        db = fixtures.open_test_database()
        db.mk_dir("my_dir1").set_value("my_entry", "my_value")
        db.save()

        db = fixtures.open_test_database()
        value = db.cd_dir("my_dir1").get_value("my_entry").value

        self.assertEqual("my_value", value)

    def test_db_with_file(self):
        db = fixtures.open_test_database()
        db.mk_dir("my_dir2").put_file("file.txt", "File content".encode("utf-8"))
        db.save()

        db = fixtures.open_test_database()
        file_entry = db.cd_dir("my_dir2").get_file("file.txt")

        self.assertEqual(file_entry.filename, "file.txt")
        self.assertEqual(file_entry.contents, "File content".encode("utf-8"))

    def test_find_entry_by_path(self):
        db = fixtures.open_test_database()
        db.mk_dir("my_dir3").set_value("my_entry3", "my_value3")
        db.mk_dir("my_dir3").put_file("test.txt", "contents".encode("utf-8"))

        entry = db.get_entry("/my_dir3/my_entry3")
        self.assertIsInstance(entry, KeyValue)
        self.assertEqual(entry.name, "my_entry3")

        entry = db.get_entry("/my_dir3")
        self.assertIsInstance(entry, Folder)
        self.assertEqual(entry.name, "my_dir3")

        entry = db.get_entry("/my_dir3/test.txt")
        self.assertIsInstance(entry, File)
        self.assertEqual(entry.name, "test.txt")

        self.assertIsNone(db.get_entry("/my_dir3/not-found"))
        self.assertIsNone(db.get_entry("/not-found/entry.txt"))
        self.assertIsNone(db.get_entry("/not-found"))
