import shlex
from subprocess import CompletedProcess, PIPE, STDOUT
from sys import executable
from unittest import TestCase
from unittest.mock import Mock, patch

from freezegun import freeze_time

from fdbk import DictConnection
from fdbk.builtin.parallel_exec import main, FAILED_CONNECTION, TOPIC_CREATION_FAILED

COMMON_ARGS = ['--db-connection', 'dict']


class ParallelExecTest(TestCase):
    def _create_topic(self, name, cmd, db_connection=None):
        argv = [*COMMON_ARGS, 'create', '-N', name, '--start-in', '0', '--repeat-for', '0.5', '-c', *cmd]
        with patch('sys.argv', argv):
            main()

        topics = db_connection.get_topics(template='execution')
        self.assertEqual(len(topics), 1)

        topic_d = topics[0]
        self.assertEqual(topic_d['name'], name)
        self.assertEqual(topic_d['metadata']['command'], cmd)

        return topic_d['id']

    def _execute(self, name, *args):
        with patch('sys.argv', [*COMMON_ARGS, 'exec', '-N', name, *args]):
            main()

    @patch('builtins.print')
    @patch('fdbk.builtin.parallel_exec._should_repeat', side_effect=[True, True, False])
    @patch('fdbk.builtin.parallel_exec.run')
    @patch('fdbk.builtin.parallel_exec.create_db_connection', return_value=DictConnection())
    def test_main(self, create_mock, run_mock, repeat_mock, print_mock):
        C = create_mock.return_value

        name = 'Test execution'
        cmd = ['sleep', '5']
        topic_id = self._create_topic(name, cmd, C)

        # Execute
        process = CompletedProcess(cmd, 0, b'asd')
        run_mock.return_value = process

        self._execute(name)

        run_mock.assert_called_with(cmd, stderr=STDOUT, stdout=PIPE)
        self.assertEqual(len(run_mock.mock_calls), 2)
        self.assertEqual(len(C.get_data(topic_id)), 2)

        console = C.get_data(topic_id)[0]["output"]
        self.assertIn('+ sleep 5', console)

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

        name = 'Test execution'
        cmd = [
            executable or 'python',
            '-c',
            'import sys, time;'
            'print("out");'
            'time.sleep(0.5);'
            'print("err", file=sys.stderr);'
        ]

        topic_id = self._create_topic(name, cmd, C)

        self._execute(name, '--console-as-json')

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