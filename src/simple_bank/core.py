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
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import ClassVar, Literal, final


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


class Result(Enum):
    OK = "ok"
    DUPLICATE = "duplicate"
    INSUFFICIENT_BALANCE = "insufficient-balance"
    UNKNOWN_ACCOUNT = "unknown-account"


InitBalanceResult = Literal[Result.OK, Result.DUPLICATE]
TransferResult = (
    Literal[Result.OK, Result.INSUFFICIENT_BALANCE]
    | tuple[Literal[Result.UNKNOWN_ACCOUNT], Account]
)


@final
class CompanyAccounts:
    """Class to manage the accounts for a company."""

    def __init__(self) -> None:
        self._balances: dict[Account, Money] = dict()

    def init_balance(self, account: Account, balance: Money) -> InitBalanceResult:
        """Set the initial balance for an account.

        Return:
        - `Result.DUPLICATE` if the account already exists.
        - `Result.OK` if all is well.
        """
        if account in self._balances:
            return Result.DUPLICATE

        self._balances[account] = balance
        return Result.OK

    def transfer(self, src: Account, dest: Account, amount: Money) -> TransferResult:
        """Transfer `amount` from `src` to `dest` account.

        Return:
        - `(Result.UNKNOWN_ACCOUNT, account)` if either account doesn't exist.
        - `Result.INSUFFICIENT_BALANCE` if the `src` account doesn't have enough money.
        - `Result.OK` if all is well.
        """
        src_cur_bal = self._balances.get(src)
        if not src_cur_bal:
            return (Result.UNKNOWN_ACCOUNT, src)

        dest_cur_bal = self._balances.get(dest)
        if not dest_cur_bal:
            return (Result.UNKNOWN_ACCOUNT, dest)

        match Money.subtract(src_cur_bal, amount):
            case None:
                return Result.INSUFFICIENT_BALANCE

            case src_new_bal:
                self._balances[src] = src_new_bal
                self._balances[dest] = Money.add(dest_cur_bal, amount)
                return Result.OK

    def balances(self) -> Iterable[tuple[Account, Money]]:
        """Yield all (account, balance) pairs."""
        for account, balance in self._balances.items():
            yield account, balance
