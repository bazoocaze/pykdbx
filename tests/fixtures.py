import os.path
from unittest.mock import Mock

import pykeepass
from pykeepass import PyKeePass

from src import database

TEST_KDBX = "test.kdbx"
DEFAULT_PASS = "123"


def create_test_kdbx():
    db = pykeepass.create_database(TEST_KDBX, password=DEFAULT_PASS)
    db.save()
    return db


def create_test_database():
    create_database = database.create_database(TEST_KDBX, password=DEFAULT_PASS)
    create_database.save()
    return create_database


def open_test_database():
    return database.open_database(TEST_KDBX, password=DEFAULT_PASS)


def args_fixture(database_path=TEST_KDBX, password=DEFAULT_PASS, keyfile="", source="", destination="",
                 entry_path=None, entry_value=None, output_file=""):
    args = Mock()
    args.database_path = database_path
    args.password = password
    args.keyfile = keyfile
    args.source = source
    args.destination = destination
    args.entry_path = entry_path
    args.entry_path = entry_path
    args.entry_value = entry_value
    args.output_file = output_file
    return args


def cache_fixture():
    cache = Mock()
    cache.data = {}
    return cache


def out_fixture():
    out = Mock()
    out.write = Mock()
    return out


def remove_all():
    files = ["test.txt", TEST_KDBX]
    for file in files:
        remove_file(file)


def remove_file(file):
    if os.path.exists(file):
        os.remove(file)


def open_test_kdbx():
    return PyKeePass(TEST_KDBX, password=DEFAULT_PASS)
