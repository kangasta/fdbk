from unittest import TestCase
from unittest.mock import Mock, patch

from fdbk.utils import get_connection_argparser, get_reporter_argparser

class ReporterArgparserTest(TestCase):
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
