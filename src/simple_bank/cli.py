"""CLI for the simple bank processor."""

from argparse import ArgumentParser
from pathlib import Path
import sys


def _parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Process bank transfers from CSV files.",
    )
    _ = parser.add_argument(
        "-i",
        "--input-balances-file",
        required=True,
        type=Path,
        help="Path to input account balances CSV",
    )
    _ = parser.add_argument(
        "-t",
        "--transactions-file",
        required=True,
        type=Path,
        help="Path to transactions CSV",
    )
    _ = parser.add_argument(
        "-o",
        "--output-balances-file",
        required=True,
        type=Path,
        help="Path to output account balances CSV",
    )

    return parser


def main() -> int:
    args = _parser().parse_args()

    return 0


if __name__ == "__main__":
    sys.exit(main())
