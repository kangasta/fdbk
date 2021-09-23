import os
from unittest import TestCase
from uuid import uuid4

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from fdbk import DictConnection
from fdbk.utils import CommonTest

class DictConnectionCommonTest(CommonTest, TestCase):
    def setUp(self):
        self.C = DictConnection()

class DictConnectionTest(TestCase):
    def test_topics_backup_saves_dict_to_file(self):
        filename = f'{uuid4()}.json'
        C1 = DictConnection(f'/tmp/{filename}')
        C1.add_topic('Test topic 1')
        C1.add_topic('Test topic 2')

        C2 = DictConnection(f'/tmp/{filename}')
        topics = C2.get_topics()

        os.remove(f'/tmp/{filename}')

        self.assertEqual(len(topics), 2)

    def test_get_topics_raises_keyerror_on_template_not_found(self):
        C = DictConnection()
        C.add_topic('test_template', type_str='template')
        C.add_topic('topic', template='test_template')

        C.get_topics()

        C._topics.pop('test_template')
        with self.assertRaises(KeyError):
            C.get_topics()
