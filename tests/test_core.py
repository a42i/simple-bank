# NOTE: Raw asserts are to keep the typechecker happy only.

import unittest
from decimal import Decimal
from typing import ClassVar, override

from simple_bank.core import Account, CompanyAccounts, Money, Result
from tests import util


class TestAccount(unittest.TestCase):
    # There is little value in trying to test that the `re` module works as advertised; focus on
    # ensuring we are using the "right" pattern.

    def test_parse_invalid(self) -> None:
        cases = [
            "",
            "0123456789123",    # < 16 digits
            "a123456789123456", # non digit chars
            "-012345678912345", # sign present
        ]

        for case in cases:
            with self.subTest(f"{case=}"):
                self.assertIsNone(Account.parse(case))

    def test_parse_valid(self) -> None:
        value = "0123456789123456"
        account = util.account(value)

        self.assertEqual(value, Account.serialise(account))

    def test_serialise(self) -> None:
        account = util.account("0123456789123456")

        self.assertEqual(account, Account.parse(Account.serialise(account)))

    def test_constructor_fails(self) -> None:
        with self.assertRaises(TypeError):
            _ = Account("0123456789123456")


class TestMoney(unittest.TestCase):
    # As above, focus on simple canary tests to ensure we haven't made any easily avoidable mistakes.

    def test_parse_invalid(self) -> None:
        cases = [
            "",
            "1",                # nothing after decimal
            "1.0",              # < 2 digits after decimal
            "1.000",            # > 2 digits after decimal
            "-1.00",            # signed value
            "+1.00",            # signed value
            "1.a0",             # non-numeric
            ".00",              # nothing before the decimal
        ]

        for case in cases:
            with self.subTest("f{case=}"):
                self.assertIsNone(Money.parse(case))

    def test_parse_valid(self) -> None:
        cases = [
            "0.00",
            "1.05",
            "100.99",
        ]

        for case in cases:
            with self.subTest(f"{case=}"):
                money = util.money(case)

                self.assertEqual(case, Money.serialise(money))

    def test_serialise(self) -> None:
        money = util.money("10.99")

        self.assertEqual(money, Money.parse(Money.serialise(money)))

    def test_add(self) -> None:
        cases = [
            # (a, b, c = a + b)
            ("1.00", "0.00", "1.00"),
            ("0.00", "1.00", "1.00"),
            ("1.00", "2.00", "3.00"),
            ("99.99", "0.01", "100.00"),
        ]

        for val_a, val_b, val_c in cases:
            with self.subTest(f"{val_a=}, {val_b=}"):
                a = util.money(val_a)
                b = util.money(val_b)

                c = Money.add(a, b)
                assert c is not None

                self.assertEqual(val_c, Money.serialise(c))

    def test_subtract_valid(self) -> None:
        cases = [
            # (a, b, c = a - b : a > b)
            ("1.00", "0.00", "1.00"),
            ("1.00", "1.00", "0.00"),
            ("3.00", "2.00", "1.00"),
            ("100.00", "0.01", "99.99"),
        ]

        for val_a, val_b, val_c in cases:
            with self.subTest(f"{val_a=}, {val_b=}"):
                a = util.money(val_a)
                b = util.money(val_b)

                c = Money.subtract(a, b)
                assert c is not None

                self.assertEqual(val_c, Money.serialise(c))

    def test_subtract_invalid(self) -> None:
        cases = [
            ("0.00", "0.01"),
            ("1.00", "1.01"),
        ]

        for val_a, val_b in cases:
            with self.subTest(f"{val_a=}, {val_b=}"):
                a = util.money(val_a)
                b = util.money(val_b)

                self.assertIsNone(Money.subtract(a, b))

    def test_constructor_raises(self) -> None:
        with self.assertRaises(TypeError):
            _ = Money(Decimal("10.00"))


class TestCompanyAccounts(unittest.TestCase):
    ACCOUNT_1: ClassVar[Account] = util.account("0000000000000001")
    ACCOUNT_2: ClassVar[Account] = util.account("0000000000000002")

    @override
    def setUp(self) -> None:
        self.accounts = CompanyAccounts()

    def test_init_balance_ok(self) -> None:
        result = self.accounts.init_balance(self.ACCOUNT_1, util.money("10.00"))

        self.assertEqual(Result.OK, result)

    def test_init_balance_duplicate(self) -> None:
        _ = self.accounts.init_balance(self.ACCOUNT_1, util.money("10.00"))
        result = self.accounts.init_balance(self.ACCOUNT_1, util.money("20.00"))

        self.assertEqual(Result.DUPLICATE, result)

    def test_init_balance_duplicate_preserves_original(self) -> None:
        _ = self.accounts.init_balance(self.ACCOUNT_1, util.money("10.00"))
        _ = self.accounts.init_balance(self.ACCOUNT_1, util.money("20.00"))
        balances = dict(self.accounts.balances())

        self.assertEqual("10.00", Money.serialise(balances[self.ACCOUNT_1]))

    def test_transfer_ok(self) -> None:
        _ = self.accounts.init_balance(self.ACCOUNT_1, util.money("10.00"))
        _ = self.accounts.init_balance(self.ACCOUNT_2, util.money("5.00"))
        result = self.accounts.transfer(
            self.ACCOUNT_1, self.ACCOUNT_2, util.money("3.00")
        )

        self.assertEqual(Result.OK, result)

    def test_transfer_updates_balances(self) -> None:
        _ = self.accounts.init_balance(self.ACCOUNT_1, util.money("10.00"))
        _ = self.accounts.init_balance(self.ACCOUNT_2, util.money("5.00"))
        _ = self.accounts.transfer(self.ACCOUNT_1, self.ACCOUNT_2, util.money("3.00"))
        balances = dict(self.accounts.balances())

        self.assertEqual("7.00", Money.serialise(balances[self.ACCOUNT_1]))
        self.assertEqual("8.00", Money.serialise(balances[self.ACCOUNT_2]))

    def test_transfer_full_balance(self) -> None:
        _ = self.accounts.init_balance(self.ACCOUNT_1, util.money("10.00"))
        _ = self.accounts.init_balance(self.ACCOUNT_2, util.money("0.00"))
        result = self.accounts.transfer(
            self.ACCOUNT_1, self.ACCOUNT_2, util.money("10.00")
        )

        self.assertEqual(Result.OK, result)

    def test_transfer_insufficient_balance(self) -> None:
        _ = self.accounts.init_balance(self.ACCOUNT_1, util.money("5.00"))
        _ = self.accounts.init_balance(self.ACCOUNT_2, util.money("0.00"))
        result = self.accounts.transfer(
            self.ACCOUNT_1, self.ACCOUNT_2, util.money("5.01")
        )

        self.assertEqual(Result.INSUFFICIENT_BALANCE, result)

    def test_transfer_insufficient_balance_preserves_balances(self) -> None:
        _ = self.accounts.init_balance(self.ACCOUNT_1, util.money("5.00"))
        _ = self.accounts.init_balance(self.ACCOUNT_2, util.money("2.00"))
        _ = self.accounts.transfer(self.ACCOUNT_1, self.ACCOUNT_2, util.money("5.01"))
        balances = dict(self.accounts.balances())

        self.assertEqual("5.00", Money.serialise(balances[self.ACCOUNT_1]))
        self.assertEqual("2.00", Money.serialise(balances[self.ACCOUNT_2]))

    def test_transfer_unknown_src(self) -> None:
        _ = self.accounts.init_balance(self.ACCOUNT_2, util.money("5.00"))
        result = self.accounts.transfer(
            self.ACCOUNT_1, self.ACCOUNT_2, util.money("1.00")
        )

        self.assertEqual((Result.UNKNOWN_ACCOUNT, self.ACCOUNT_1), result)

    def test_transfer_unknown_dest(self) -> None:
        _ = self.accounts.init_balance(self.ACCOUNT_1, util.money("5.00"))
        result = self.accounts.transfer(
            self.ACCOUNT_1, self.ACCOUNT_2, util.money("1.00")
        )

        self.assertEqual((Result.UNKNOWN_ACCOUNT, self.ACCOUNT_2), result)

    def test_balances_empty(self) -> None:
        self.assertEqual([], list(self.accounts.balances()))

    def test_balances_returns_all(self) -> None:
        _ = self.accounts.init_balance(self.ACCOUNT_1, util.money("10.00"))
        _ = self.accounts.init_balance(self.ACCOUNT_2, util.money("5.00"))
        balances = dict(self.accounts.balances())

        self.assertIsNotNone(balances[self.ACCOUNT_1])
        self.assertIsNotNone(balances[self.ACCOUNT_2])
