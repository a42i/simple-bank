
from collections.abc import Iterable
import csv
from typing import TextIO
from simple_bank.codec import ReadBalanceResult, Balance, InputError
from simple_bank.core import Account, Money

def read_balances(input: TextIO) -> Iterable[ReadBalanceResult]:
    """Treat `input` as a CSV file object and read balance records from it.

    If `input` is a file object, it must have been opened with `newline=''`. Refer to
    https://docs.python.org/3/library/csv.html#csv.reader for more details.
    """
    for line, row in enumerate(csv.reader(input), start=1):
        match row:
            case [account_str, amount_str]:
                account = Account.parse(account_str.strip())
                amount = Money.parse(amount_str.strip())

                if account is None:
                    yield InputError(line, f"invalid account '{account_str}'")

                if amount is None:
                    yield InputError(line, f"invalid amount '{amount_str}'")

                if account is not None and amount is not None:
                    yield Balance(account, amount)

            case _:
                yield InputError(line, f"expected 2 columns, got {len(row)}")
