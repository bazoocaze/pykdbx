import os.path
import sys

import pykeepass
from pykeepass import PyKeePass
from pykeepass.attachment import Attachment
from pykeepass.entry import Entry
from pykeepass.group import Group


class DatabaseEntry:
    @property
    def name(self) -> str:
        pass

    def delete(self):
        pass


class KeyValue(DatabaseEntry):
    def __init__(self, kdb: PyKeePass, entry: Entry):
        self._kdb = kdb
        self._entry = entry

    def __str__(self):
        return "KeyValue(name={})".format(self._entry.title)

    def __repr__(self):
        return self.__str__()

    @property
    def name(self) -> str:
        return self._entry.title

    @property
    def value(self):
        return self._entry.password

    @value.setter
    def value(self, input_value):
        self._entry.password = input_value

    def delete(self):
        self._entry.delete()


class File(DatabaseEntry):
    def __init__(self, kdb: PyKeePass, entry: Entry, attachment: Attachment):
        self._kdb = kdb
        self._entry = entry
        self._attachment = attachment

    @property
    def name(self):
        return self.filename

    @property
    def filename(self) -> str:
        return self._attachment.filename

    @property
    def contents(self):
        return self._attachment.binary

    @contents.setter
    def contents(self, value):
        self._kdb.delete_binary(self._attachment.id)
        self._attachment.id = self._kdb.add_binary(value)

    def delete(self):
        self._attachment.delete()
        if not self._entry.attachments:
            self._entry.delete()

    def __str__(self):
        return "File(filename={})".format(self._attachment.filename)

    def __repr__(self):
        return self.__str__()


class Folder(DatabaseEntry):
    def __init__(self, kdb: PyKeePass, kdb_group: Group):
        self._kdb = kdb
        self._kdb_group = kdb_group

    @property
    def name(self) -> str:
        return "/" if self._kdb_group.is_root_group else self._kdb_group.name

    def set_value(self, name: str, value: str):
        if not name:
            raise Exception("Invalid name for entry")
        for item in self.entries():
            if isinstance(item, KeyValue) and item.name == name:
                item.value = value
                return
        entry = self._kdb.add_entry(self._kdb_group, title=name, username="", password=value)
        return KeyValue(self._kdb, entry)

    def get_value(self, name: str):
        for item in self.entries():
            if isinstance(item, KeyValue) and item.name == name:
                return item
        return None

    def entries(self):
        for item in self._kdb_group.subgroups:
            yield Folder(self._kdb, item)
        for item in self._kdb_group.entries:
            if item.username or item.password or not item.attachments:
                yield KeyValue(self._kdb, item)
            for attachment in item.attachments:
                yield File(self._kdb, item, attachment)

    def put_file(self, filename: str, contents: bytes):
        if not filename:
            raise Exception("Invalid filename")
        for entry in self.entries():
            if isinstance(entry, File) and entry.filename == filename:
                entry.contents = contents
                return
        entry = self._kdb.add_entry(self._kdb_group, title=filename, username="", password="")
        bin_id = self._kdb.add_binary(contents)
        entry.add_attachment(bin_id, filename=filename)

    def get_file(self, filename: str):
        for entry in self.entries():
            if isinstance(entry, File) and entry.filename == filename:
                return entry
        return None

    def delete(self):
        self._kdb_group.delete()

    def __str__(self):
        name = "/" if self._kdb_group.is_root_group else self._kdb_group.name
        return "Directory(name={})".format(name)

    def __repr__(self):
        return self.__str__()


class Database:
    def __init__(self, kdb):
        self._kdb = kdb

    @property
    def root_directory(self):
        return Folder(self._kdb, kdb_group=self._kdb.root_group)

    def save(self):
        self._kdb.save()

    def mk_dir(self, target_path: str):
        path_parts = self._normalize_path(target_path).split("/")
        current_group = self._kdb.root_group
        if path_parts and path_parts[0]:
            for path_name in path_parts:
                if not path_name:
                    raise Exception("Invalid path part: {}".format(target_path))
                groups = {sg.name for sg in current_group.subgroups}
                if path_name not in groups:
                    current_group = self._kdb.add_group(current_group, path_name)
                else:
                    current_group = self._kdb.find_groups(path=current_group.path + [path_name])
        return Folder(self._kdb, current_group)

    def cd_dir(self, target_path: str):
        target_path = self._normalize_path(target_path)
        result = self._kdb.find_groups(path=target_path.split("/"))
        if result:
            return Folder(self._kdb, result)
        return None

    def get_entry(self, entry_path: str):
        directory_name = os.path.dirname(entry_path)
        directory = self.cd_dir(directory_name)
        if directory:
            for entry in directory.entries():
                if entry.name.lower() == os.path.basename(entry_path).lower():
                    return entry
            sys.stderr.write("WARN: entry not found: {}\n".format(entry_path))
        else:
            sys.stderr.write("WARN: directory not found: {}\n".format(directory_name))
        return None

    @staticmethod
    def _normalize_path(input_path) -> str:
        if input_path.startswith("/"):
            input_path = input_path[1:]
        if input_path.endswith("/"):
            input_path = input_path[:-1]
        return input_path


def open_database(filename: str, password: str = None, keyfile: str = None):
    kdb = PyKeePass(filename=filename, password=password, keyfile=keyfile)
    return Database(kdb)


def create_database(filename: str, password=None, keyfile=None):
    kdb = pykeepass.create_database(filename, password=password, keyfile=keyfile)
    return Database(kdb)
