from subprocess import CompletedProcess, PIPE, STDOUT
from unittest import TestCase
from unittest.mock import Mock, patch

from freezegun import freeze_time

from fdbk import DictConnection
from fdbk.builtin.parallel_exec import main, FAILED_CONNECTION, TOPIC_CREATION_FAILED

COMMON_ARGS = ['--db-connection', 'dict']


class ParallelExecTest(TestCase):
    @patch('builtins.print')
    @patch('fdbk.builtin.parallel_exec._should_repeat', side_effect=[True, True, False])
    @patch('fdbk.builtin.parallel_exec.run')
    @patch('fdbk.builtin.parallel_exec.create_db_connection', return_value=DictConnection())
    def test_main(self, create_mock, run_mock, repeat_mock, print_mock):
        C = create_mock.return_value

        # Create topic
        name = 'Test execution'
        cmd = ['sleep', '5']
        with patch('sys.argv', [*COMMON_ARGS, 'create', '-N', name, '--start-in', 0, '-c', *cmd]):
            main()

        topics = C.get_topics(template='execution')
        self.assertEqual(len(topics), 1)

        topic_d = topics[0]
        topic_id = topic_d['id']
        self.assertEqual(topic_d['name'], name)
        self.assertEqual(topic_d['metadata']['command'], cmd)

        # Execute
        process = CompletedProcess(cmd, 0, b'asd')
        run_mock.return_value = process

        with patch('sys.argv', [*COMMON_ARGS, 'exec', '-N', name]):
            main()

        run_mock.assert_called_with(cmd, stderr=STDOUT, stdout=PIPE)
        self.assertEqual(len(run_mock.mock_calls), 2)
        self.assertEqual(len(C.get_data(topic_id)), 2)

    @patch('builtins.exit')
    @patch('builtins.print')
    @patch('fdbk.builtin.parallel_exec.create_db_connection')
    def test_main_create_error(self, create_mock, print_mock, exit_mock):
        create_mock.return_value.add_topic.side_effect = RuntimeError

        name = 'Test execution'
        cmd = ['sleep', '5']
        with patch('sys.argv', [*COMMON_ARGS, 'create', '-N', name, '--start-in', 0, '-c', *cmd]):
            main()

        exit_mock.assert_called_with(TOPIC_CREATION_FAILED)
