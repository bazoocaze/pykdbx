import os
import sys

from src import password_generator, config, database
from src.database import KeyValue, File


class App:
    def __init__(self, args, cache, out=sys.stdout, stdin=sys.stdin):
        self.args = args
        self.cache = cache
        self.out = out
        self.stdin = stdin

    def create(self):
        database_path = self._resolve_database_path()
        password = self.args.password or password_generator.generate(config.CONFIG["generate_password_size"])
        keyfile = self.args.keyfile

        if not os.path.exists(database_path):
            db = database.create_database(database_path, password=password, keyfile=keyfile)
            db.save()
            self.out.write("Database created: {}\n".format(database_path))
        else:
            sys.stderr.write("Database already exists: {}\n".format(database_path))
            return False

        self.cache.data.setdefault("databases", {}).setdefault(database_path, {})["password"] = password
        self.cache.data["last_database"] = database_path
        self.cache.save()
        return True

    def set_entry(self):
        db = self._open_database()
        directory = db.mk_dir(os.path.dirname(self.args.entry_path))
        directory.set_value(os.path.basename(self.args.entry_path), self.args.entry_value)
        db.save()
        self._update_cache()

    def get_entry(self):
        db = self._open_database()
        entry_path = self.args.entry_path
        entry = db.get_entry(entry_path)
        if entry and isinstance(entry, KeyValue):
            self.out.write("{}\n".format(entry.value))
            self._update_cache()
            return entry
        sys.stderr.write("ERROR: key value not found: {}\n".format(entry_path))
        return None

    def get_file(self):
        db = self._open_database()
        source = self.args.source
        entry = db.get_entry(source)
        if entry and isinstance(entry, File):
            if self.args.output_file:
                with open(self._resolve_path(self.args.output_file), "bw") as f:
                    f.write(entry.contents)
            else:
                self.out.write("{}".format(entry.contents.decode("utf-8")))
            self._update_cache()
            return entry
        sys.stderr.write("ERROR: file not found: {}\n".format(source))
        return None

    def put_file(self):
        with open(self._resolve_path(self.args.source), "br") as f:
            db = self._open_database()
            data = f.read()
            target_dir = db.mk_dir(self.args.destination) if self.args.destination else db.root_directory
            target_dir.put_file(os.path.basename(self.args.source), data)
            db.save()
            self._update_cache()

    def _open_database(self):
        database_path = self._resolve_database_path()
        password = self._resolve_password(database_path)
        keyfile = self.args.keyfile or self._cache_get_database_entry(database_path, "keyfile")
        return database.open_database(filename=database_path, password=password, keyfile=keyfile)

    def _resolve_database_path(self):
        database_path = self.args.database_path or self.cache.data.get("last_database")
        if not database_path:
            raise Exception("Database filename not informed")
        return os.path.abspath(self._resolve_path(database_path))

    def _cache_get_database_entry(self, database_path: str, entry_name: str):
        return self.cache.data.get("databases", {}).get(database_path, {}).get(entry_name)

    def ls_entries(self):
        db = self._open_database()
        source = self.args.source
        directory = db.cd_dir(source)
        if directory:
            number_of_entries = 0
            for entry in directory.entries():
                self.out.write("{}\n".format(entry))
                number_of_entries += 1
            self.out.write("{} entries\n".format(number_of_entries))
            self._update_cache()
        else:
            sys.stderr.write("ERROR: directory not found: {}\n".format(source))
        return directory

    def del_entry(self):
        db = self._open_database()
        entry_path = self.args.entry_path
        entry = db.get_entry(entry_path)
        if entry:
            self.out.write("Removing entry: {}\n".format(entry))
            entry.delete()
            db.save()
            self._update_cache()
            return entry
        sys.stderr.write("ERROR: entry not found: {}\n".format(entry_path))
        return None

    def _update_cache(self):
        database_path = self._resolve_database_path()
        password = self.args.password or self._cache_get_database_entry(database_path, "password")
        keyfile = self.args.keyfile or self._cache_get_database_entry(database_path, "keyfile")
        self.cache.data["last_database"] = database_path
        self.cache.data.setdefault("databases", {}).setdefault(database_path, {})["password"] = password
        self.cache.data.setdefault("databases", {}).setdefault(database_path, {})["keyfile"] = keyfile
        self.cache.save()

    def _resolve_path(self, input_path):
        if self.args.curdir:
            return os.path.abspath(os.path.join(self.args.curdir, input_path))
        return input_path

    def _resolve_password(self, database_path: str):
        password = self.args.password or self._cache_get_database_entry(database_path, "password")
        if not password:
            self.out.write("Please inform the password:\n")
            typed_password = self.stdin.readline()
            if typed_password.endswith('\n'):
                typed_password = typed_password[:-1]
            self.args.password = typed_password
            return typed_password
        return password
