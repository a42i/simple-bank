"""CLI for the simple bank processor.

This module takes a very simplistic approach to error handling in order to save some time; it raises
an error and crashes. This would definitely not be something we should do in a real system, unless
we're on the Beam.

"""

import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Literal, TextIO, cast

from simple_bank import csv_codec
from simple_bank.codec import Balance, InputError, Transaction
from simple_bank.core import CompanyAccounts, Result


class ProgramError(Exception):
    """Generic exception raised on any error."""

    pass


def main() -> int:
    args = _parser().parse_args()

    with (
        _open(args.input_balances_file) as input_balances,
        _open(args.transactions_file) as input_transactions,
        _open(args.output_balances_file, "w") as output_balances,
    ):
        exit_code = run(input_balances, input_transactions, output_balances)
        if not exit_code:
            print("Completed.")
        return exit_code


def run(
    input_balances: TextIO, input_transactions: TextIO, output_balances: TextIO
) -> int:

    accounts = CompanyAccounts()

    _read_input_balances(input_balances, accounts)
    _apply_input_transactions(input_transactions, accounts)

    balances = (Balance(account, money) for (account, money) in accounts.balances())
    csv_codec.write_balances(output_balances, balances)

    return 0


def _apply_input_transactions(input: TextIO, accounts: CompanyAccounts) -> None:
    for txn in csv_codec.read_transactions(input):
        match txn:
            case Transaction(src, dest, amount):
                match accounts.transfer(src, dest, amount):
                    case Result.OK:
                        pass
                    case Result.INSUFFICIENT_BALANCE:
                        raise ProgramError(
                            f"(input transactions):transfer:insufficient {src=}, {dest=}, {amount=}"
                        )
                    case (Result.UNKNOWN_ACCOUNT, account):
                        raise ProgramError(
                            f"(input transactions):transfer:unknown {account=}"
                        )

            case InputError(line, msg):
                raise ProgramError(f"(input transactions):read:{line=}, {msg=}")


def _read_input_balances(input: TextIO, accounts: CompanyAccounts) -> None:
    for balance in csv_codec.read_balances(input):
        match balance:
            case Balance(account, amount):
                match accounts.init_balance(account, amount):
                    case Result.OK:
                        pass
                    case Result.DUPLICATE:
                        raise ProgramError(
                            f"(input balances):init:duplicate {account=}"
                        )

            case InputError(line, msg):
                raise ProgramError(f"(input balances):read:{line=}, {msg=}")


def _open(path: Path, mode: Literal["r", "w"] = "r") -> TextIO:
    return cast(TextIO, open(path, mode, newline="", encoding="utf-8"))


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


if __name__ == "__main__":
    sys.exit(main())
