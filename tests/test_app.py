from unittest import TestCase
from unittest.mock import Mock

import fixtures
from fixtures import args_fixture, cache_fixture, out_fixture
from src.app import App
from src.database import KeyValue, Folder


class TestApp(TestCase):

    def setUp(self) -> None:
        fixtures.remove_all()

    def tearDown(self) -> None:
        fixtures.remove_all()

    def test_create(self):
        fixtures.remove_file("test.kdbx")
        args = args_fixture(database_path="test.kdbx")
        cache = cache_fixture()
        app = App(args, cache)

        app.create()

        db = fixtures.open_test_database()
        self.assertEqual(list(db.root_directory.entries()).__len__(), 0)

    def test_get_value(self):
        db = fixtures.create_test_database()
        db.mk_dir("the_dir").set_value("entry_name", "entry_value")
        db.save()
        args = args_fixture(entry_path="the_dir/entry_name")
        cache = cache_fixture()
        out = out_fixture()
        app = App(args, cache, out)

        result = app.get_entry()

        self.assertEqual(result.name, "entry_name")
        self.assertEqual(result.value, "entry_value")
        out.write.assert_called_with("entry_value\n")

    def test_set_value(self):
        fixtures.create_test_database()
        args = args_fixture(entry_path="the_dir/entry_name", entry_value="entry_value")
        cache = cache_fixture()
        app = App(args, cache)

        app.set_entry()

        db = fixtures.open_test_database()
        entry = db.cd_dir("the_dir").get_value("entry_name")
        self.assertEqual(entry.name, "entry_name")
        self.assertEqual(entry.value, "entry_value")

    def test_put_file(self):
        self._create_file("test.txt", "File contents")
        args = args_fixture(source="test.txt", destination="the_dir")
        cache = cache_fixture()
        fixtures.create_test_kdbx()
        app = App(args, cache)

        app.put_file()

        db = fixtures.open_test_kdbx()
        group = db.find_groups(name="the_dir", first=True)
        self.assertEqual(group.entries[0].title, "test.txt")
        self.assertEqual(group.entries[0].attachments[0].filename, "test.txt")
        self.assertEqual(group.entries[0].attachments[0].binary, "File contents".encode("utf-8"))

    def test_get_file(self):
        db = fixtures.create_test_kdbx()
        group = db.add_group(db.root_group, "the_dir")
        entry = db.add_entry(group, title="file.txt", username="", password="")
        entry.add_attachment(db.add_binary("Content".encode("utf-8")), filename="file.txt")
        db.save()
        args = args_fixture(source="the_dir/file.txt")
        cache = cache_fixture()
        app = App(args, cache)

        result = app.get_file()

        self.assertEqual(result.filename, "file.txt")
        self.assertEqual(result.contents, "Content".encode("utf-8"))

    def test_ls(self):
        db = fixtures.create_test_database()
        db.mk_dir("/the_dir").set_value("item_name", "item_value")
        db.save()
        args = args_fixture(source="/the_dir")
        cache = cache_fixture()
        out = fixtures.out_fixture()
        app = App(args, cache, out)

        result = app.ls_entries()

        self.assertIsInstance(result, Folder)
        self.assertEqual(result.name, "the_dir")
        out.write: Mock
        self.assertEqual(out.write.call_count, 2)
        self.assertRegex(out.write.call_args_list[0].args[0], ".*item_name.*")
        self.assertRegex(out.write.call_args_list[1].args[0], "1 entries.*")

    def test_del_entry(self):
        db = fixtures.create_test_database()
        db.root_directory.set_value("the_value", "content")
        db.save()
        args = args_fixture(entry_path="the_value")
        cache = cache_fixture()
        app = App(args, cache)

        result = app.del_entry()

        self.assertTrue(isinstance(result, KeyValue))
        db = fixtures.open_test_database()
        self.assertIsNone(db.root_directory.get_value("the_value"))

    @staticmethod
    def _create_file(filename, contents: str):
        with open(filename, "w") as f:
            f.write(contents)
            f.flush()
