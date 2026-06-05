import csv
from collections.abc import Iterable
from typing import TextIO

from simple_bank.codec import (
    BalanceRecord,
    InvalidInput,
    ReadBalanceResult,
    ReadTransactionResult,
    TransactionRecord,
)
from simple_bank.core import Account, Money


def read_balances(input: TextIO) -> Iterable[ReadBalanceResult]:
    """Treat `input` as an open CSV file and read balance records from it.

    If `input` actually is a file object, it must have been opened with `newline=''`. Refer to
    https://docs.python.org/3/library/csv.html#csv.reader for more details.
    """
    for line, row in enumerate(csv.reader(input), start=1):
        match row:
            case [account_str, amount_str]:
                account = Account.parse(account_str.strip())
                amount = Money.parse(amount_str.strip())

                if account is None:
                    yield InvalidInput(line, f"invalid account '{account_str}'")

                if amount is None:
                    yield InvalidInput(line, f"invalid amount '{amount_str}'")

                if account is not None and amount is not None:
                    yield BalanceRecord(account, amount)

            case _:
                yield InvalidInput(line, f"expected 2 columns, got {len(row)}")


def write_balances(output: TextIO, balances: Iterable[BalanceRecord]) -> None:
    """Treat `output` as an open CSV file and write balance records to it.

    If `output` actually is a file object, it must have been opened with `newline=''`. Refer to
    https://docs.python.org/3/library/csv.html#csv.reader for more details.
    """
    writer = csv.writer(output)
    for account, amount in balances:
        writer.writerow((Account.serialise(account), Money.serialise(amount)))


def read_transactions(input: TextIO) -> Iterable[ReadTransactionResult]:
    """Treat `input` as an open CSV file and read transaction records from it.

    If `input` actually is a file object, it must have been opened with `newline=''`. Refer to
    https://docs.python.org/3/library/csv.html#csv.reader for more details.
    """
    for line, row in enumerate(csv.reader(input), start=1):
        match row:
            case [src_str, dst_str, amount_str]:
                src = Account.parse(src_str.strip())
                dest = Account.parse(dst_str.strip())
                amount = Money.parse(amount_str.strip())

                if src is None:
                    yield InvalidInput(line, f"invalid source account '{src_str}'")

                if dest is None:
                    yield InvalidInput(line, f"invalid destination account '{dst_str}'")

                if amount is None:
                    yield InvalidInput(line, f"invalid amount '{amount_str}'")

                if not (src is None or dest is None or amount is None):
                    yield TransactionRecord(src, dest, amount)

            case _:
                yield InvalidInput(line, f"expected 3 columns, got {len(row)}")
