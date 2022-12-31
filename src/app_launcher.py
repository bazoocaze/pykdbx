import argparse
import sys

from src.app import App
from src.cache import Cache


def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", type=str, metavar="password", help="password for kdbx file", dest="password")
    parser.add_argument("-f", type=str, metavar="database", help="kdbx filename", dest="database_path")
    parser.add_argument("-k", type=str, metavar="keyfile", help="kdbx secret keyfile", dest="keyfile")
    parser.add_argument("--curdir", type=str)
    command_parser = parser.add_subparsers(dest="command", title="commands", required=True)
    create_command = command_parser.add_parser("create", help="create database")
    ls_command = command_parser.add_parser("ls", help="list entries")
    ls_command.add_argument("source", help="source path")
    put_file_command = command_parser.add_parser("put-file", help="copy file into database")
    put_file_command.add_argument("source", help="source file")
    put_file_command.add_argument("destination", help="destination path")
    get_file_command = command_parser.add_parser("get-file", help="copy file from database")
    get_file_command.add_argument("source", help="path to file")
    get_file_command.add_argument("-o", metavar="output_file", dest="output_file")
    set_command = command_parser.add_parser("set", help="set value to KeyValue")
    set_command.add_argument("entry_path", help="path to KeyValue")
    set_command.add_argument("entry_value", help="new value for KeyValue")
    get_command = command_parser.add_parser("get", help="get value from KeyValue")
    get_command.add_argument("entry_path", help="path to KeyValue")
    del_command = command_parser.add_parser("del", help="delete entry")
    del_command.add_argument("entry_path", help="entry path to delete")
    return parser


def parse_args(args=None):
    parser = create_arg_parser()
    return parser.parse_args(args)


def run(args=None):
    args = parse_args(args)
    app = App(args, Cache(), sys.stdout)
    if args.command == "create":
        if not app.create():
            return 1
    elif args.command == "ls":
        if not app.ls_entries():
            return 1
    elif args.command == "put-file":
        app.put_file()
    elif args.command == "get-file":
        if not app.get_file():
            return 1
    elif args.command == "set":
        app.set_entry()
    elif args.command == "get":
        if not app.get_entry():
            return 1
    elif args.command == "del":
        if not app.del_entry():
            return 1
    else:
        sys.stderr.write("ERROR: no command informed\n")
    return 0
