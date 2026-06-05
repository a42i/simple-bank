# NOTE: Raw asserts are to keep the typechecker happy only.

import unittest
from decimal import Decimal

from simple_bank.core import Account, Money


def _account(value: str) -> Account:
    """Internal helper that assumes `value` is always valid."""
    account = Account.parse(value)
    assert account is not None
    return account


def _money(value: str) -> Money:
    """Internal helper that assumes `value` is always valid."""
    money = Money.parse(value)
    assert money is not None
    return money


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
        account = _account(value)

        self.assertEqual(value, Account.serialise(account))

    def test_serialise(self) -> None:
        account = _account("0123456789123456")

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
                money = _money(case)

                self.assertEqual(case, Money.serialise(money))

    def test_serialise(self) -> None:
        money = _money("10.99")

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
                a = _money(val_a)
                b = _money(val_b)

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
                a = _money(val_a)
                b = _money(val_b)

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
                a = _money(val_a)
                b = _money(val_b)

                self.assertIsNone(Money.subtract(a, b))

    def test_constructor_raises(self) -> None:
        with self.assertRaises(TypeError):
            _ = Money(Decimal("10.00"))
