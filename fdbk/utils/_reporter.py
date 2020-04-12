from argparse import ArgumentParser

from ._connection import get_connection_argparser


def get_reporter_argparser(parser=None):
    if not parser:
        parser = ArgumentParser()

    get_connection_argparser(parser)
    parser.add_argument(
        "--interval",
        "-i",
        type=float,
        help="Data pushing interval in seconds.")
    parser.add_argument(
        "--num-samples",
        "-n",
        type=int,
        help="Number of samples to average during the push interval")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print progress messages")

    return parser
