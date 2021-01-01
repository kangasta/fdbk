import shlex
from subprocess import CompletedProcess, PIPE, STDOUT
from sys import executable
from unittest import TestCase
from unittest.mock import Mock, patch

from freezegun import freeze_time

from fdbk import DictConnection
from fdbk.builtin.parallel_exec import main, FAILED_CONNECTION, TOPIC_CREATION_FAILED

COMMON_ARGS = ['--db-connection', 'dict']
TEST_EXEC_NAME = "Test execution"

class ParallelExecTest(TestCase):
    def _create_topic(self, name, cmd, db_connection=None):
        argv = [*COMMON_ARGS, 'create', '-N', name, '--start-in', '0', '--repeat-for', '0.5', '-c', *cmd]
        with patch('sys.argv', argv):
            main()

        topics = db_connection.get_topics(template='execution')
        self.assertEqual(len(topics), 1)

        topic_d = topics[0]
        self.assertEqual(topic_d['name'], f'{name} #1')
        self.assertEqual(topic_d['metadata']['command'], cmd)

        return topic_d['id']

    def _execute(self, name, *args):
        with patch('sys.argv', [*COMMON_ARGS, 'exec', '-N', name, *args]):
            main()

    @patch('builtins.print')
    @patch('fdbk.builtin.parallel_exec._should_repeat', side_effect=[True, True, True, False])
    @patch('fdbk.builtin.parallel_exec.run')
    @patch('fdbk.builtin.parallel_exec.create_db_connection', return_value=DictConnection())
    def test_main(self, create_mock, run_mock, repeat_mock, print_mock):
        C = create_mock.return_value

        cmd = ['sleep', '5']
        topic_id = self._create_topic(TEST_EXEC_NAME, cmd, C)

        topics = C.get_topics(template='execution')
        self.assertEqual(len(topics), 1)

        topic_d = topics[0]
        topic_id = topic_d['id']
        self.assertEqual(topic_d['name'], f'{TEST_EXEC_NAME} #1')
        self.assertEqual(topic_d['metadata']['command'], cmd)

        # Execute
        process = CompletedProcess(cmd, 0, b'asd')
        run_mock.return_value = process

        self._execute(TEST_EXEC_NAME)

        run_mock.assert_called_with(cmd, stderr=STDOUT, stdout=PIPE)
        self.assertEqual(len(run_mock.mock_calls), 2)
        self.assertEqual(len(C.get_data(topic_id)), 2)

        console = C.get_data(topic_id)[0]["output"]
        self.assertIn('+ sleep 5', console)

    @patch('builtins.print')
    @patch('fdbk.builtin.parallel_exec.create_db_connection', return_value=DictConnection())
    def test_main_suffix(self, create_mock, print_mock):
        C = create_mock.return_value

        # Create topics
        for name, repeat_for in [
            (TEST_EXEC_NAME, '0'),
            (TEST_EXEC_NAME, '0.1'),
            ('Another test', '1'),
        ]:
            cmd = ['sleep', '0.1']
            with patch('sys.argv', [*COMMON_ARGS, 'create', '-N', name, '--start-in', '0', '--repeat-for', repeat_for, '-c', *cmd]):
                main()

        topic_ids = [i.get('id') for i in C.get_topics(template='execution')]
        self.assertEqual(len(topic_ids), 3)

        self._execute(TEST_EXEC_NAME)

        self.assertEqual(len(C.get_data(topic_ids[0])), 0)
        self.assertGreaterEqual(len(C.get_data(topic_ids[1])), 1)
        self.assertEqual(len(C.get_data(topic_ids[2])), 0)

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

    @patch('builtins.print')
    @patch('fdbk.builtin.parallel_exec.create_db_connection', return_value=DictConnection())
    def test_json_console(self, create_mock, print_mock):
        C = create_mock.return_value

        cmd = [
            executable or 'python',
            '-c',
            'import sys, time;'
            'print("out");'
            'time.sleep(0.5);'
            'print("err", file=sys.stderr);'
        ]

        topic_id = self._create_topic(TEST_EXEC_NAME, cmd, C)

        self._execute(TEST_EXEC_NAME, '--console-as-json')

        self.assertEqual(len(C.get_data(topic_id)), 1)
        console = C.get_data(topic_id)[0]['output']
        self.assertEqual(len(console), 3)
        self.assertEqual(shlex.split(console[0]['text']), cmd)

        for stream, text in [
            ('stdout', 'out'),
            ('stderr', 'err'),
        ]:
            msg = next(i for i in console if i['stream'] == stream)

            self.assertEqual(msg['stream'], stream, f'Stream: {stream}')
            self.assertEqual(msg['text'], text, f'Stream: {stream}')