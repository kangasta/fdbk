from unittest import TestCase
from unittest.mock import Mock, patch

from fdbk.utils import (
    create_db_connection,
    get_connection_argparser,
    get_reporter_argparser,
    process_db_parameters)

class UtilsTest(TestCase):
    def test_interval_and_num_samples_default_to_none(self):
        parser = get_reporter_argparser()
        args = parser.parse_args([])

        self.assertIsNone(args.interval)
        self.assertIsNone(args.num_samples)

    def test_parsers_db_connection_details(self):
        for parser in (get_connection_argparser(), get_reporter_argparser(), ):
            in_ = ["http://localhost:8080"]
            args = parser.parse_args(in_)
            self.assertEqual(args.db_parameters, in_)

            in_ = ["--db-connection", "fdbk_dynamodb_plugin"]
            args = parser.parse_args(in_)
            self.assertEqual(args.db_parameters, [])
            self.assertEqual(args.db_connection, "fdbk_dynamodb_plugin")

    def test_process_db_parameters(self):
        args, kwargs = process_db_parameters([
            "asd",
            "qwe=asd",
            "zxc=qwe=asd",
        ])

        self.assertEqual(len(args), 1)
        self.assertEqual(len(kwargs), 2)

        self.assertEqual(args[0], "asd")
        self.assertEqual(kwargs["qwe"], "asd")
        self.assertEqual(kwargs["zxc"], "qwe=asd")

    def test_create_db_connection(self):
        backup = "/home/user/.fdbk-topics.json"
        c = create_db_connection("dict", [f"topics_db_backup={backup}"])
        self.assertEqual(c._topics_backup, backup)
