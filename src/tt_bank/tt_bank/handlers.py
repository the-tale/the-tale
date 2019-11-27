import datetime

from tt_web import log
from tt_web import handlers
from tt_web import exceptions as tt_exceptions

from tt_protocol.protocol import bank_pb2

from . import protobuf
from . import operations
from . import exceptions


@handlers.api(bank_pb2.AccountsBalancesRequest)
async def accounts_balances(message, **kwargs):
    balances = await operations.load_balances(accounts_ids=message.accounts_ids)
    return bank_pb2.AccountsBalancesResponse(balances={account_id: protobuf.from_balances(amounts)
                                                       for account_id, amounts in balances.items()})


@handlers.api(bank_pb2.AccountHistoryRequest)
async def account_history(message, **kwargs):
    history = await operations.load_history(account_id=message.account_id)
    return bank_pb2.AccountHistoryResponse(history=[protobuf.from_history(record) for record in history])


@handlers.api(bank_pb2.StartTransactionRequest)
async def start_transaction(message, **kwargs):
    logger = log.ContextLogger()

    try:
        transaction_id = await operations.start_transaction(operations=[protobuf.to_operation(operation)
                                                                        for operation in message.operations],
                                                            lifetime=datetime.timedelta(seconds=message.lifetime),
                                                            autocommit=message.autocommit,
                                                            restrictions=protobuf.to_restrictions(message.restrictions),
                                                            logger=logger)

    except exceptions.NoOperationsInTransaction as e:
        raise tt_exceptions.ApiError(code='bank.start_transaction.no_operations_specified', message=str(e))

    except exceptions.BalanceChangeExceededRestrictions as e:
        raise tt_exceptions.ApiError(code='bank.start_transaction.restrictions_exceeded', message=str(e))

    return bank_pb2.StartTransactionResponse(transaction_id=transaction_id)


@handlers.api(bank_pb2.CommitTransactionRequest)
async def commit_transaction(message, **kwargs):
    logger = log.ContextLogger()

    try:
        await operations.commit_transaction(transaction_id=message.transaction_id,
                                            logger=logger)
    except exceptions.NoTransactionToCommit as e:
        raise tt_exceptions.ApiError(code='bank.commit_transaction.no_transacton_to_commit', message=str(e))

    except exceptions.BalanceChangeExceededRestrictions as e:
        raise tt_exceptions.ApiError(code='bank.start_transaction.restrictions_exceeded', message=str(e))

    return bank_pb2.CommitTransactionResponse()


@handlers.api(bank_pb2.RollbackTransactionRequest)
async def rollback_transaction(message, **kwargs):
    logger = log.ContextLogger()

    try:
        await operations.rollback_transaction(transaction_id=message.transaction_id,
                                              logger=logger)
    except exceptions.NoTransactionToRollback as e:
        raise tt_exceptions.ApiError(code='bank.rollback_transaction.no_transacton_to_rollback', message=str(e))

    except exceptions.BalanceChangeExceededRestrictions as e:
        raise tt_exceptions.ApiError(code='bank.start_transaction.restrictions_exceeded', message=str(e))

    return bank_pb2.RollbackTransactionResponse()


@handlers.api(bank_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_database()
    return bank_pb2.DebugClearServiceResponse()
