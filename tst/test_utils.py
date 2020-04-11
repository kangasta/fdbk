from unittest import TestCase
from unittest.mock import Mock, patch

from fdbk.utils import get_reporter_argparser

class ReporterArgparserTest(TestCase):
    def test_interval_and_num_samples_default_to_none(self):
        parser = get_reporter_argparser()
        args = parser.parse_args([])

        self.assertIsNone(args.interval)
        self.assertIsNone(args.num_samples)