from argparse import ArgumentParser, REMAINDER
from datetime import datetime, timedelta
from subprocess import run, PIPE, STDOUT
from time import sleep

from dateutil.parser import isoparse

from fdbk.utils.messages import created_topic
from fdbk.utils import (
    get_connection_argparser,
    create_db_connection,
    timestamp_as_str)
from fdbk import Reporter


def timestamp(timestamp_dt=None):
    if not timestamp_dt:
        timestamp_dt = datetime.utcnow()

    return timestamp_as_str(timestamp_dt)


STARTED_UNIT = dict(field='started', unit='iso_8601')
ELAPSED_UNIT = dict(field='elapsed', unit='seconds')
OUTPUT_UNIT = dict(field='output', unit='console')


def _elapsed_list_params(method):
    return dict(parameters=dict(name='Elapsed statistics', method=method))


MIN_ELAPSED = dict(
    field='elapsed', method='list_item', **_elapsed_list_params('min'))
AVERAGE_ELAPSED = dict(
    field='elapsed', method='list_item', **_elapsed_list_params('average'))
MEDIAN_ELAPSED = dict(
    field='elapsed', method='list_item', **_elapsed_list_params('median'))
MAX_ELAPSED = dict(
    field='elapsed', method='list_item', **_elapsed_list_params('max'))

LINE_ELAPSED = dict(field='elapsed', method='line')
PIE_EXIT_STATUS = dict(field='exit_status', method='doughnut')

TEMPLATE_NAME = "execution"
TEMPLATE_DICT = dict(
    name=TEMPLATE_NAME,
    type_str="template",
    description="Execution result.",
    fields=['started', 'elapsed', 'exit_status', 'output'],
    units=[STARTED_UNIT, ELAPSED_UNIT, OUTPUT_UNIT],
    data_tools=[
        MIN_ELAPSED,
        AVERAGE_ELAPSED,
        MEDIAN_ELAPSED,
        MAX_ELAPSED,
        LINE_ELAPSED,
        PIE_EXIT_STATUS,
    ],
)


def create_topic_dict(name, command, repeat_for=60, start_in=15):
    repeat_since = datetime.utcnow() + timedelta(seconds=start_in)
    repeat_until = datetime.utcnow() + timedelta(seconds=start_in + repeat_for)

    metadata = dict(
        command=command,
        repeat_since=timestamp(repeat_since),
        repeat_until=timestamp(repeat_until),
    )

    return dict(
        name=name,
        template="execution",
        type_str="topic",
        metadata=metadata,
    )


def create_topic(db_connection, name, command, repeat_for=60, start_in=15):
    topic_d = create_topic_dict(name, command, repeat_for, start_in)
    db_connection.add_topic(**TEMPLATE_DICT, overwrite=True)
    topic_id = db_connection.add_topic(**topic_d)
    return {**topic_d, 'id': topic_id}


def wait_for_topic(db_connection, name, interval=2):
    while True:
        topics = db_connection.get_topics(template=TEMPLATE_NAME)
        try:
            topic_d = next(i for i in topics if i.get('name') == name)
            return topic_d
        except Exception:
            sleep(interval)


def _get_execution(topic_d):
    metadata = topic_d.get('metadata')
    command = metadata.get('command')
    repeat_since = isoparse(metadata.get('repeat_since')).replace(tzinfo=None)
    repeat_until = isoparse(metadata.get('repeat_until')).replace(tzinfo=None)

    return command, repeat_since, repeat_until


def _should_start(repeat_since):
    return datetime.utcnow() >= repeat_since


def _should_repeat(repeat_until):
    return datetime.utcnow() < repeat_until


def _wait_for_start(repeat_since, interval=2):
    while not _should_start(repeat_since):
        sleep(interval)


def execute(db_connection, name, verbose=False, interval=2):
    print(f'Waiting for execution topic with name {name}.')
    topic_d = wait_for_topic(db_connection, name, interval)
    topic_id = topic_d.get('id')
    print(f'Found topic {topic_id}.')

    reporter = Reporter(
        db_connection=db_connection, topic_id=topic_id, verbose=verbose)

    command, since, until = _get_execution(topic_d)
    print(f'Waiting for execution to start at {timestamp(since)}.')
    _wait_for_start(since, interval)
    print(f'Repeating command until {timestamp(until)}.')
    while _should_repeat(until):
        started = datetime.utcnow()
        process = run(command, stderr=STDOUT, stdout=PIPE)
        elapsed = (datetime.utcnow() - started).total_seconds()

        data = dict(
            started=timestamp(started),
            elapsed=elapsed,
            exit_status=process.returncode,
            output=process.stdout.decode('utf-8'),
        )

        reporter.push(data)

    print(f'Execution finished at {timestamp()}.')


def get_argparser():
    name_parser = ArgumentParser(add_help=False)
    name_parser.add_argument(
        "--name",
        "-N",
        type=str,
        default='default',
        help="Execution name.")

    parser = get_connection_argparser()
    subparsers = parser.add_subparsers(dest='sub_command')

    create_parser = subparsers.add_parser(
        'create',
        help='Create parallel execution',
        parents=[name_parser])
    exec_parser = subparsers.add_parser(
        'exec',
        help='Execute parallel execution',
        parents=[name_parser])

    create_parser.add_argument(
        '--command',
        '-c',
        nargs=REMAINDER,
        help="Command to execute. Takes in all of the remaining arguments.")
    create_parser.add_argument(
        "--repeat-for",
        type=float,
        default=60,
        help="Repeat command for given number of seconds.")
    create_parser.add_argument(
        "--start-in",
        type=float,
        default=15,
        help="Start repeating command in given number of seconds.")

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print progress messages")

    return parser


NO_COMMAND = 1
EXEC_INTERRUPTED = 2
FAILED_CONNECTION = 3
TOPIC_CREATION_FAILED = 4


def main():
    parser = get_argparser()
    args = parser.parse_args()

    try:
        db_connection = create_db_connection(
            args.db_connection, args.db_parameters)
    except Exception as error:
        print(str(error))
        exit(FAILED_CONNECTION)

    if args.sub_command == 'create':
        try:
            topic_d = create_topic(
                db_connection,
                args.name,
                args.command,
                args.repeat_for,
                args.start_in)
            print(created_topic(topic_d))
        except Exception:
            print('Creating topic failed.')
            exit(TOPIC_CREATION_FAILED)
    elif args.sub_command == 'exec':
        try:
            execute(db_connection, args.name, args.verbose)
        except KeyboardInterrupt:
            exit(EXEC_INTERRUPTED)
    else:
        print('No command specified.')
        exit(NO_COMMAND)


if __name__ == '__main__':
    main()
