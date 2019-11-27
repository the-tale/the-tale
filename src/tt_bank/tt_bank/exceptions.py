from tt_web import exceptions


class BankError(exceptions.BaseError):
    pass


class NoOperationsInTransaction(BankError):
    MESSAGE = 'There are no operations in transaction'


class NoTransactionToRollback(BankError):
    MESSAGE = 'Transaction {transaction_id} not found or not in OPENED state'


class NoTransactionToCommit(BankError):
    MESSAGE = 'Transaction {transaction_id} not found or not in COMMITED state'


class BalanceChangeExceededRestrictions(BankError):
    MESSAGE = 'balance change exceed transaction restrictions'
