import json
import os
import sys

from src import config


class Cache:
    def __init__(self):
        self._data: dict = None
        self._file_name = self._get_cache_file_name()
        self._data_hash = None
        self._mark_not_changed()

    @staticmethod
    def _get_cache_file_name():
        if os.environ.__contains__("XDG_RUNTIME_DIR"):
            return "{}/{}".format(os.environ["XDG_RUNTIME_DIR"], config.CONFIG["cache_file_name"])
        if os.getuid():
            directory = "/run/user/{}".format(os.getuid())
            if os.path.exists(directory):
                return directory
        return None

    def _load(self):
        if self._file_name and os.path.exists(self._file_name):
            try:
                with open(self._file_name, "r") as f:
                    self._data = json.load(f)
                    self._mark_not_changed()
            except Exception as ex:
                sys.stderr.write("WARN: failed to load state file [{}]: {}\n".format(self._file_name, ex.__str__()))

    def save(self):
        if self._file_name and self._is_changed():
            with open(self._file_name, "w") as f:
                try:
                    json.dump(self._data, f)
                    self._mark_not_changed()
                except Exception as ex:
                    sys.stderr.write("WARN: failed to save state file [{}]: {}\n".format(self._file_name, ex.__str__()))

    @property
    def data(self) -> dict:
        if self._data is None:
            self._data = {}
            self._load()
        return self._data

    def _calculate_hash_of_data(self):
        if self._data:
            return json.dumps(self._data).__hash__()
        return "".__hash__()

    def _is_changed(self):
        return self._data_hash != self._calculate_hash_of_data()

    def _mark_not_changed(self):
        self._data_hash = self._calculate_hash_of_data()
