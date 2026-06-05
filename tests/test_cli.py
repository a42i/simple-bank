from collections.abc import Iterable
import csv
from io import StringIO
from typing import TextIO
import unittest

from simple_bank import cli, csv_codec
from simple_bank.codec import TransactionRecord, BalanceRecord
from simple_bank.core import Account, Money


class TestCLIRun(unittest.TestCase):
    @staticmethod
    def _invert_transactions(
        txns: Iterable[TransactionRecord],
    ) -> Iterable[TransactionRecord]:
        """Returns the "inverse" of a set of transactions.

        i.e. the sequence of transactions, that reverses the affect of `txns`.

        """
        for src, dest, amount in reversed(list(txns)):
            yield TransactionRecord(dest, src, amount)

    @staticmethod
    def _read_transactions(input: TextIO) -> Iterable[TransactionRecord]:
        for txn in csv_codec.read_transactions(input):
            match txn:
                case TransactionRecord():
                    yield txn
                case _:
                    pass

    @staticmethod
    def _read_balances(input: TextIO) -> Iterable[BalanceRecord]:
        for balance in csv_codec.read_balances(input):
            match balance:
                case BalanceRecord():
                    yield balance
                case _:
                    pass

    def test_apply_then_reverse_transactions(self) -> None:
        # Verify that we end up with the same balances when we apply some transactions, and then apply
        # their inverse.
        #
        # This is also an excellent candicate for a property based test, but that is likely overkill
        # for this exercise.

        # The inputs for this test are from the coding challenge bundle.

        input_balances = StringIO(
            "\n".join(
                [
                    "1111234522226789,5000.00",
                    "1111234522221234,10000.00",
                    "2222123433331212,550.00",
                    "1212343433335665,1200.00",
                    "3212343433335755,50000.00",
                ]
            )
        )

        input_transactions = StringIO(
            "\n".join(
                [
                    "1111234522226789,1212343433335665,500.00",
                    "3212343433335755,2222123433331212,1000.00",
                    "3212343433335755,1111234522226789,320.50",
                    "1111234522221234,1212343433335665,25.60",
                ]
            )
        )

        # Apply `input_transactions` to `input_balances` to get the `output_balances`.
        output_balances = StringIO()
        _ = cli.run(input_balances, input_transactions, output_balances)

        # Generate inverse transactions and write them to `reversed_transactions`.
        _ = input_transactions.seek(0)
        reversed_transactions = StringIO()
        csv_codec.write_transactions(
            reversed_transactions,
            self._invert_transactions(self._read_transactions(input_transactions)),
        )

        # Apply `reversed_transactions` to `output_balances` to get `next_balances`.
        _ = output_balances.seek(0)
        _ = reversed_transactions.seek(0)
        next_balances = StringIO()
        _ = cli.run(output_balances, reversed_transactions, next_balances)

        # Now, `input_balances` and `next_balances` "should" be the same if there aren't any bugs in
        # our code.
        _ = input_balances.seek(0)
        _ = next_balances.seek(0)

        self.assertDictEqual(
            dict(self._read_balances(input_balances)),
            dict(self._read_balances(next_balances)),
        )
