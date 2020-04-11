from argparse import ArgumentParser


def get_reporter_argparser(parser=None):
    if not parser:
        parser = ArgumentParser()

    parser.add_argument(
        "db_parameters",
        nargs="*",
        type=str,
        help="Parameters for fdbk DB connection.")
    parser.add_argument(
        "--db-connection",
        type=str,
        default="ClientConnection",
        help="fdbk DB connection to use (default=ClientConnection)")
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
