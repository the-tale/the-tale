from tt_web import exceptions


class BankError(exceptions.BaseError):
    pass


class NoOperationsInTransaction(BankError):
    MESSAGE = 'There are no operations in transaction'


class NoEnoughCurrency(BankError):
    MESSAGE = 'Account {account_id} has no enough currency for amount change: {amount}'


class NoTransactionToRollback(BankError):
    MESSAGE = 'Transaction {transaction_id} not found or not in OPENED state'


class NoTransactionToCommit(BankError):
    MESSAGE = 'Transaction {transaction_id} not found or not in COMMITED state'
