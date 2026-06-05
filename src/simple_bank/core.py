"""Core domain classes.

The goal is for all the code in this module to be IO free. We also indicate errors by returning
suitable values, leaving the caller to decide how to deal with those errors. In some cases, the only
sensible action for the caller may be to terminate the program.
"""

# https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html#forward-references
# Also see https://docs.python.org/3/reference/compound_stmts.html#annotations
from __future__ import annotations

import decimal
import re
from dataclasses import dataclass
from decimal import Decimal
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


@final
@dataclass(frozen=True)
class Money:
    """Immutable Money implementation."""

    _amount: Decimal

    _PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"\d+\.\d{2}")
    _SENTINEL: ClassVar[object] = object()
    _CENT: ClassVar[Decimal] = Decimal("0.01")  # used for quantization only

    # Setup our own context so we can trap most errors, but still use half-even rounding. It
    # is better to fail than give bad results.
    #
    # Refer to https://docs.python.org/3/library/decimal.html#decimal.BasicContext
    _CONTEXT: ClassVar[decimal.Context] = decimal.BasicContext.copy()
    _CONTEXT.rounding = decimal.ROUND_HALF_EVEN

    def __init__(self, _amount: Decimal, _sentinel: object = None) -> None:
        if _sentinel is not Money._SENTINEL:
            raise TypeError("Use Money.parse() to create Money instances")
        object.__setattr__(self, "_amount", _amount.quantize(Money._CENT))

    @staticmethod
    def add(x: Money, y: Money) -> Money:
        """Return a new `Money` object with a value of `x + y`."""
        result = Money._CONTEXT.add(x._amount, y._amount)
        return Money(result, Money._SENTINEL)

    @staticmethod
    def subtract(x: Money, y: Money) -> Money | None:
        """Return a new `Money` object with a value of `x - y`.

        Since there isn't such a thing as "negative" money, return `None` if `y` is greater than `x`.
        """
        result = Money._CONTEXT.subtract(x._amount, y._amount)
        if result.is_signed():
            return None
        return Money(result, Money._SENTINEL)

    @staticmethod
    def parse(value: str) -> Money | None:
        """Parse `value` into Money, if possible."""
        if Money._PATTERN.fullmatch(value):
            return Money(Decimal(value), Money._SENTINEL)
        return None

    @staticmethod
    def serialise(money: Money) -> str:
        """Return a string representation of the Money object.

        The returned value is always parse-able by `parse`.
        """
        return str(money._amount)
