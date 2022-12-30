import os.path
from unittest import TestCase

import fixtures
from src import app_launcher


class TestAppLauncher(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        fixtures.remove_all()

    @classmethod
    def tearDownClass(cls) -> None:
        fixtures.remove_all()

    def test_create_arg_parser(self):
        parser = app_launcher.create_arg_parser()
        assert parser.parse_args(args=["create"]).command == "create"

    def test_run_create_command(self):
        result = app_launcher.run(args=["-f", fixtures.TEST_KDBX, "-p", fixtures.DEFAULT_PASS, "create"])
        assert result == 0
        assert os.path.exists(fixtures.TEST_KDBX)
