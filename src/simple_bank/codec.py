"""Common types for all codecs.

A codec is a module that reads/writes balance files and reads transaction files.
"""
from typing import NamedTuple
from simple_bank.core import Account, Money

class BalanceRecord(NamedTuple):
    account: Account
    amount: Money

class InvalidInput(NamedTuple):
    line: int
    # In a serious system, we would use a tagged union, so callers can decide what action to take
    # depending on the type of error. Trying to match error messages is less than ideal.
    msg: str


ReadBalanceResult = InvalidInput | BalanceRecord

class Transaction(NamedTuple):
    src: Account
    dest: Account
    amount: Money

ReadTransactionResult = InvalidInput | Transaction
