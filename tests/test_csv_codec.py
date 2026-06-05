# NOTE: Raw asserts are to keep the typechecker happy only.

import io
from typing import ClassVar
import unittest

from simple_bank.codec import Balance, InputError, ReadBalanceResult
from simple_bank.csv_codec import read_balances
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
            [Balance(util.account(self._ACCOUNT1), util.money(self._AMOUNT1))],
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
                Balance(util.account(self._ACCOUNT1), util.money(self._AMOUNT1)),
                Balance(util.account(account2), util.money(amount2)),
            ],
        )

    def test_strips_whitespace(self) -> None:
        self.assertEqual(
            self._read_balances(f" {self._ACCOUNT1} , {self._AMOUNT1} "),
            [Balance(util.account(self._ACCOUNT1), util.money(self._AMOUNT1))],
        )

    def test_invalid_account(self) -> None:
        [result] = self._read_balances(f"bad,{self._AMOUNT1}")
        assert isinstance(result, InputError)

        self.assertEqual(result.line, 1)

    def test_invalid_amount(self) -> None:
        [result] = self._read_balances(f"{self._ACCOUNT1},bad")
        assert isinstance(result, InputError)

        self.assertEqual(result.line, 1)

    def test_invalid_account_and_amount(self) -> None:
        results = self._read_balances("bad,bad")

        self.assertEqual(len(results), 2)

        for result in results:
            assert isinstance(result, InputError)

            self.assertEqual(result.line, 1)

    def test_too_few_columns(self) -> None:
        [result] = self._read_balances(self._ACCOUNT1)
        assert isinstance(result, InputError)

        self.assertEqual(result.line, 1)

    def test_too_many_columns(self) -> None:
        [result] = self._read_balances(f"{self._ACCOUNT1},{self._AMOUNT1},extra")
        assert isinstance(result, InputError)

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
            results[0], Balance(util.account(self._ACCOUNT1), util.money(self._AMOUNT1))
        )

        e1, e2 = results[1], results[2]
        assert isinstance(e1, InputError) and isinstance(e2, InputError)

        self.assertEqual(e1.line, 2)
        self.assertEqual(e2.line, 2)
        self.assertEqual(
            results[3], Balance(util.account(self._ACCOUNT1), util.money(self._AMOUNT1))
        )
