import os
from unittest import TestCase

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from fdbk import DictConnection

from common_tests import tests

class DictConnectionTest(TestCase):
    def test_run_common_tests(self):
        for test in tests:
            C = DictConnection()
            test(self, C)

    def test_topics_backup_saves_dict_to_file(self):
        C1 = DictConnection('/tmp/asd.json')
        C1.add_topic('Test topic 1')
        C1.add_topic('Test topic 2')

        C2 = DictConnection('/tmp/asd.json')
        topics = C2.get_topics()

        os.remove('/tmp/asd.json')

        self.assertEqual(len(topics), 2)
