# NOTE: Raw asserts are to keep the typechecker happy only.

import io
import unittest
from typing import ClassVar

from simple_bank.codec import (
    BalanceRecord,
    InvalidInput,
    ReadBalanceResult,
    ReadTransactionResult,
    Transaction,
)
from simple_bank.csv_codec import read_balances, read_transactions, write_balances
from tests import util


class TestReadBalances(unittest.TestCase):
    # There is little value in checking the error messages; it leads to unnecessary coupling between
    # the tests and the code. It will also make life unnecessarily complicated if/when we have to
    # worry about internationalisation.

    _ACCOUNT1: ClassVar[str] = "1000000000000000"
    _AMOUNT1: ClassVar[str] = "1.00"

    @staticmethod
    def _read_balances(text: str) -> list[ReadBalanceResult]:
        return list(read_balances(io.StringIO(text)))

    def test_empty_input(self) -> None:
        self.assertEqual(self._read_balances(""), [])

    def test_valid_single_row(self) -> None:
        self.assertEqual(
            self._read_balances(f"{self._ACCOUNT1},{self._AMOUNT1}"),
            [BalanceRecord(util.account(self._ACCOUNT1), util.money(self._AMOUNT1))],
        )

    def test_valid_multiple_rows(self) -> None:
        account2 = "2000000000000000"
        amount2 = "2.00"
        results = self._read_balances(
            f"{self._ACCOUNT1},{self._AMOUNT1}\n{account2},{amount2}"
        )

        self.assertEqual(
            results,
            [
                BalanceRecord(util.account(self._ACCOUNT1), util.money(self._AMOUNT1)),
                BalanceRecord(util.account(account2), util.money(amount2)),
            ],
        )

    def test_strips_whitespace(self) -> None:
        self.assertEqual(
            self._read_balances(f" {self._ACCOUNT1} , {self._AMOUNT1} "),
            [BalanceRecord(util.account(self._ACCOUNT1), util.money(self._AMOUNT1))],
        )

    def test_invalid_account(self) -> None:
        [result] = self._read_balances(f"bad,{self._AMOUNT1}")
        assert isinstance(result, InvalidInput)

        self.assertEqual(result.line, 1)

    def test_invalid_amount(self) -> None:
        [result] = self._read_balances(f"{self._ACCOUNT1},bad")
        assert isinstance(result, InvalidInput)

        self.assertEqual(result.line, 1)

    def test_invalid_account_and_amount(self) -> None:
        results = self._read_balances("bad,bad")

        self.assertEqual(len(results), 2)

        for result in results:
            assert isinstance(result, InvalidInput)

            self.assertEqual(result.line, 1)

    def test_too_few_columns(self) -> None:
        [result] = self._read_balances(self._ACCOUNT1)
        assert isinstance(result, InvalidInput)

        self.assertEqual(result.line, 1)

    def test_too_many_columns(self) -> None:
        [result] = self._read_balances(f"{self._ACCOUNT1},{self._AMOUNT1},extra")
        assert isinstance(result, InvalidInput)

        self.assertEqual(result.line, 1)

    def test_line_numbers_are_correct(self) -> None:
        results = self._read_balances(
            "\n".join(
                [
                    f"{self._ACCOUNT1},{self._AMOUNT1}",
                    "bad,bad",
                    f"{self._ACCOUNT1},{self._AMOUNT1}",
                ]
            )
        )

        self.assertEqual(len(results), 4)
        self.assertEqual(
            results[0], BalanceRecord(util.account(self._ACCOUNT1), util.money(self._AMOUNT1))
        )

        e1, e2 = results[1], results[2]
        assert isinstance(e1, InvalidInput) and isinstance(e2, InvalidInput)

        self.assertEqual(e1.line, 2)
        self.assertEqual(e2.line, 2)
        self.assertEqual(
            results[3], BalanceRecord(util.account(self._ACCOUNT1), util.money(self._AMOUNT1))
        )


class TestReadTransactions(unittest.TestCase):
    _ACCOUNT1: ClassVar[str] = "1000000000000000"
    _ACCOUNT2: ClassVar[str] = "2000000000000000"
    _AMOUNT1: ClassVar[str] = "1.00"

    @staticmethod
    def _read_transactions(text: str) -> list[ReadTransactionResult]:
        return list(read_transactions(io.StringIO(text)))

    def test_empty_input(self) -> None:
        self.assertEqual(self._read_transactions(""), [])

    def test_valid_single_row(self) -> None:
        self.assertEqual(
            self._read_transactions(
                f"{self._ACCOUNT1},{self._ACCOUNT2},{self._AMOUNT1}"
            ),
            [
                Transaction(
                    util.account(self._ACCOUNT1),
                    util.account(self._ACCOUNT2),
                    util.money(self._AMOUNT1),
                )
            ],
        )

    def test_valid_multiple_rows(self) -> None:
        account3 = "3000000000000000"
        amount2 = "2.00"
        results = self._read_transactions(
            f"{self._ACCOUNT1},{self._ACCOUNT2},{self._AMOUNT1}\n{self._ACCOUNT2},{account3},{amount2}"
        )

        self.assertEqual(
            results,
            [
                Transaction(
                    util.account(self._ACCOUNT1),
                    util.account(self._ACCOUNT2),
                    util.money(self._AMOUNT1),
                ),
                Transaction(
                    util.account(self._ACCOUNT2),
                    util.account(account3),
                    util.money(amount2),
                ),
            ],
        )

    def test_strips_whitespace(self) -> None:
        self.assertEqual(
            self._read_transactions(
                f" {self._ACCOUNT1} , {self._ACCOUNT2} , {self._AMOUNT1} "
            ),
            [
                Transaction(
                    util.account(self._ACCOUNT1),
                    util.account(self._ACCOUNT2),
                    util.money(self._AMOUNT1),
                )
            ],
        )

    def test_invalid_src(self) -> None:
        [result] = self._read_transactions(f"bad,{self._ACCOUNT2},{self._AMOUNT1}")
        assert isinstance(result, InvalidInput)

        self.assertEqual(result.line, 1)

    def test_invalid_dest(self) -> None:
        [result] = self._read_transactions(f"{self._ACCOUNT1},bad,{self._AMOUNT1}")
        assert isinstance(result, InvalidInput)

        self.assertEqual(result.line, 1)

    def test_invalid_amount(self) -> None:
        [result] = self._read_transactions(f"{self._ACCOUNT1},{self._ACCOUNT2},bad")
        assert isinstance(result, InvalidInput)

        self.assertEqual(result.line, 1)

    def test_all_fields_invalid(self) -> None:
        results = self._read_transactions("bad,bad,bad")

        self.assertEqual(len(results), 3)

        for result in results:
            assert isinstance(result, InvalidInput)

            self.assertEqual(result.line, 1)

    def test_too_few_columns(self) -> None:
        [result] = self._read_transactions(f"{self._ACCOUNT1},{self._ACCOUNT2}")
        assert isinstance(result, InvalidInput)

        self.assertEqual(result.line, 1)

    def test_too_many_columns(self) -> None:
        [result] = self._read_transactions(
            f"{self._ACCOUNT1},{self._ACCOUNT2},{self._AMOUNT1},extra"
        )
        assert isinstance(result, InvalidInput)

        self.assertEqual(result.line, 1)

    def test_line_numbers_are_correct(self) -> None:
        results = self._read_transactions(
            "\n".join(
                [
                    f"{self._ACCOUNT1},{self._ACCOUNT2},{self._AMOUNT1}",
                    "bad,bad,bad",
                    f"{self._ACCOUNT1},{self._ACCOUNT2},{self._AMOUNT1}",
                ]
            )
        )

        self.assertEqual(len(results), 5)
        self.assertEqual(
            results[0],
            Transaction(
                util.account(self._ACCOUNT1),
                util.account(self._ACCOUNT2),
                util.money(self._AMOUNT1),
            ),
        )

        e1, e2, e3 = results[1], results[2], results[3]
        assert (
            isinstance(e1, InvalidInput)
            and isinstance(e2, InvalidInput)
            and isinstance(e3, InvalidInput)
        )

        self.assertEqual(e1.line, 2)
        self.assertEqual(e2.line, 2)
        self.assertEqual(e3.line, 2)
        self.assertEqual(
            results[4],
            Transaction(
                util.account(self._ACCOUNT1),
                util.account(self._ACCOUNT2),
                util.money(self._AMOUNT1),
            ),
        )


class TestWriteBalances(unittest.TestCase):
    _ACCOUNT1: ClassVar[str] = "1000000000000000"
    _AMOUNT1: ClassVar[str] = "1.00"

    @staticmethod
    def _write_balances(balances: list[BalanceRecord]) -> str:
        output = io.StringIO()
        write_balances(output, balances)
        return output.getvalue()

    def test_empty_input(self) -> None:
        self.assertEqual(self._write_balances([]), "")

    # Manually checking the data written by `write_balances` will unnecessarily couple this test to
    # the output format. As long as we can round trip successfully, we can have enough confidence that
    # the code functions as it is supposed to.
    #
    # This is an excellent candidate for a property based test, but that is overkill for this
    # exercise.

    def test_round_trip(self) -> None:
        balances = [
            BalanceRecord(util.account(self._ACCOUNT1), util.money(self._AMOUNT1)),
            BalanceRecord(util.account("2000000000000000"), util.money("2.00")),
        ]
        output = io.StringIO()
        write_balances(output, balances)
        _ = output.seek(0)
        self.assertEqual(list(read_balances(output)), balances)
