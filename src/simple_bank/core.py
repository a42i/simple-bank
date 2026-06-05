"""Core domain classes.

The goal is for all the code in this module to be IO free. We also indicate errors by returning
suitable values, leaving the caller to decide how to deal with those errors. In some cases, the only
sensible action for the caller may be to terminate the program.
"""

# https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html#forward-references
# Also see https://docs.python.org/3/reference/compound_stmts.html#annotations
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar, final


@final
@dataclass(frozen=True)
class Account:
    """Immutable representation of an Account."""

    _value: str

    _PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"\d{16}")
    _SENTINEL: ClassVar[object] = object()

    def __init__(self, _value: str, _sentinel: object = None) -> None:
        if _sentinel is not Account._SENTINEL:
            raise TypeError("Use Account.parse() to create Account instances")
        object.__setattr__(self, "_value", _value)

    @staticmethod
    def parse(value: str) -> Account | None:
        """Parse `value` into an Account, if possible."""
        if Account._PATTERN.fullmatch(value):
            return Account(value, Account._SENTINEL)
        return None

    @staticmethod
    def serialise(account: Account) -> str:
        """Return a string representation of the Account.

        The returned value is always parse-able by `parse`.
        """
        return account._value
