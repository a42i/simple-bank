from simple_bank.core import Account, Money

def account(value: str) -> Account:
    """Internal helper that assumes `value` is always valid."""
    account = Account.parse(value)
    assert account is not None
    return account


def money(value: str) -> Money:
    """Internal helper that assumes `value` is always valid."""
    money = Money.parse(value)
    assert money is not None
    return money
