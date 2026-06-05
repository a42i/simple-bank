# NOTE: Raw asserts are to keep the typechecker happy only.

import unittest

from simple_bank.core import Account

def _mk_account(value: str) -> Account:
    """Internal helper that assumes `value` is always valid."""
    account = Account.parse(value)
    assert account
    return account

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
        parsed = _mk_account(value)

        self.assertEqual(value, Account.serialise(parsed))

    def test_serialise(self) -> None:
        parsed = _mk_account("0123456789123456")

        self.assertEqual(parsed, Account.parse(Account.serialise(parsed)))

    def test_constructor_fails(self) -> None:
        with self.assertRaises(TypeError):
            _ = Account("0123456789123456")
