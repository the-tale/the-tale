
import logging
import datetime

from psycopg2.extras import Json as PGJson

from tt_web import log
from tt_web import postgresql as db

from . import logic
from . import objects
from . import relations
from . import exceptions


async def load_balances(accounts_ids):

    results = await db.sql('SELECT account, currency, amount FROM accounts WHERE account IN %(accounts_ids)s',
                           {'accounts_ids': tuple(accounts_ids)})

    balances = {account_id: {} for account_id in accounts_ids}

    for row in results:
        balances[row['account']][row['currency']] = row['amount']

    return balances


async def load_balance(account_id):
    balances = await load_balances((account_id,))
    return balances[account_id]


async def load_history(account_id):

    results = await db.sql('''SELECT created_at, currency, amount, description
                              FROM operations
                              WHERE account=%(account_id)s
                              ORDER BY created_at''',
                           {'account_id': account_id})

    return [objects.HistoryRecord(created_at=row['created_at'],
                                  currency=row['currency'],
                                  amount=row['amount'],
                                  description=row['description'])
            for row in results]


async def start_transaction(operations, lifetime, autocommit, restrictions, logger):

    if not operations:
        raise exceptions.NoOperationsInTransaction()

    arguments = {'operations': operations,
                 'autocommit': autocommit,
                 'lifetime': lifetime,
                 'restrictions': restrictions,
                 'logger': logger}

    return await db.transaction(_start_transaction, arguments)


async def _start_transaction(execute, arguments):
    operations = arguments['operations']
    lifetime = arguments['lifetime']
    restrictions = arguments['restrictions']
    logger = arguments['logger']

    data = {'restrictions': restrictions.serialize()}

    results = await execute('''INSERT INTO transactions (state, lifetime, data, created_at, updated_at)
                               VALUES (%(state)s, %(lifetime)s, %(data)s, NOW(), NOW())
                               RETURNING id''',
                            {'state': relations.TRANSACTION_STATE.OPENED.value,
                             'data': PGJson(data),
                             'lifetime': lifetime})

    transaction_id = results[0]['id']

    logger.info('try to start transaction %s', transaction_id)

    for operation in operations:

        if operation.amount < 0:
            await _change_balance(execute,
                                  operation.account_id,
                                  operation.currency,
                                  operation.amount,
                                  restrictions=restrictions,
                                  logger=logger)

        await _save_operation(execute, transaction_id, operation, logger=logger)

    logger.info('transaction %s started', transaction_id)

    if arguments['autocommit']:
        await _commit_transaction(execute, {'transaction_id': transaction_id,
                                            'logger': logger})

    return transaction_id


def _log_no_currency(logger, account_id, currency, amount, tag):
    logger.info('[tag: %s] account %s has no enough currency %s for withdraw %s',
                tag,
                account_id,
                currency,
                amount)


def _log_balance_changed(logger, account_id, currency, amount, new_amount, tag):
    logger.info('[tag: %s] change account %s balance of currency %s for %s, new amount %s',
                tag,
                account_id,
                currency,
                amount,
                new_amount)


def _validate_amount(amount, restrictions):
    validated, amount = logic.validate_restrictions(restrictions, amount)

    if not validated:
        raise exceptions.BalanceChangeExceededRestrictions()

    return amount


async def _change_balance(execute, account_id, currency, amount, restrictions, logger):

    results = await execute('SELECT amount FROM accounts WHERE account=%(account_id)s AND currency=%(currency)s FOR UPDATE',
                            {'account_id': account_id,
                             'currency': currency})

    if not results:
        await execute('''INSERT INTO accounts (account, currency, amount, created_at, updated_at)
                         VALUES (%(account_id)s, %(currency)s, 0, NOW(), NOW())
                         ON CONFLICT DO NOTHING''',
                      {'account_id': account_id,
                       'currency': currency})

        await _change_balance(execute, account_id, currency, amount, restrictions, logger=logger)

        return

    new_balance = _validate_amount(results[0]['amount'] + amount, restrictions)

    await execute('''UPDATE accounts
                     SET amount=%(new_balance)s,
                         updated_at=NOW()
                     WHERE account=%(account_id)s AND currency=%(currency)s
                     RETURNING amount''',
                  {'account_id': account_id,
                   'currency': currency,
                   'new_balance': new_balance})

    _log_balance_changed(logger, account_id, currency, amount, new_balance, tag='has balance')


async def _save_operation(execute, transaction_id, operation, logger):
    await execute('''INSERT INTO operations (transaction, account, currency, amount, type, description, created_at)
                     VALUES (%(transaction)s, %(account)s, %(currency)s, %(amount)s, %(type)s, %(description)s, NOW())''',
                  {'transaction': transaction_id,
                   'account': operation.account_id,
                   'currency': operation.currency,
                   'amount': operation.amount,
                   'type': operation.type,
                   'description': operation.description})

    logger.info('operation registered, transaction_id %s, account_id=%s, currency=%s, amount=%s, type=%s, description=%s',
                transaction_id,
                operation.account_id,
                operation.currency,
                operation.amount,
                operation.type,
                operation.description)


async def rollback_transaction(transaction_id, logger):
    arguments = {'transaction_id': transaction_id,
                 'logger': logger}

    await db.transaction(_rollback_transaction, arguments)


async def _rollback_transaction(execute, arguments):
    transaction_id = arguments['transaction_id']
    logger = arguments['logger']

    logger.info('try to rollback transaction %s (with log saving)', transaction_id)

    results = await execute('UPDATE transactions SET state=%(new_state)s, updated_at=NOW() WHERE id=%(id)s AND state=%(old_state)s RETURNING id, data',
                            {'id': transaction_id,
                             'new_state': relations.TRANSACTION_STATE.ROLLBACKED.value,
                             'old_state': relations.TRANSACTION_STATE.OPENED.value})
    if not results:
        logger.info('can not rollback transaction %s: no transactions to rollback', transaction_id)
        raise exceptions.NoTransactionToRollback(transaction_id=transaction_id)

    restrictions = objects.Restrictions.deserialize(results[0]['data']['restrictions'])

    results = await execute('SELECT account, currency, amount FROM operations WHERE transaction=%(transaction)s',
                            {'transaction': transaction_id})

    for row in results:
        if row['amount'] < 0:
            await _change_balance(execute,
                                  row['account'],
                                  row['currency'],
                                  -row['amount'],
                                  restrictions=restrictions,
                                  logger=logger)

    await execute('DELETE FROM operations WHERE transaction=%(transaction)s',
                  {'transaction': transaction_id})

    logger.info('transaction %s rollbacked', transaction_id)


async def commit_transaction(transaction_id, logger):
    arguments = {'transaction_id': transaction_id,
                 'logger': logger}

    await db.transaction(_commit_transaction, arguments)


async def _commit_transaction(execute, arguments):
    transaction_id = arguments['transaction_id']
    logger = arguments['logger']

    logger.info('try to commit transaction %s (with log saving)', transaction_id)

    results = await execute('''UPDATE transactions
                               SET state=%(new_state)s,
                                   updated_at=NOW()
                               WHERE id=%(id)s AND state=%(old_state)s AND NOW() < created_at + lifetime
                               RETURNING id, data''',
                            {'id': transaction_id,
                             'new_state': relations.TRANSACTION_STATE.COMMITED.value,
                             'old_state': relations.TRANSACTION_STATE.OPENED.value})
    if not results:
        logger.info('can not commit transaction %s: no transactions to commit', transaction_id)
        raise exceptions.NoTransactionToCommit(transaction_id=transaction_id)

    restrictions = objects.Restrictions.deserialize(results[0]['data']['restrictions'])

    results = await execute('SELECT account, currency, amount FROM operations WHERE transaction=%(transaction)s',
                            {'transaction': transaction_id})

    for row in results:
        if row['amount'] > 0:
            await _change_balance(execute,
                                  row['account'],
                                  row['currency'],
                                  row['amount'],
                                  restrictions=restrictions,
                                  logger=logger)

    logger.info('transaction %s commited', transaction_id)


async def remove_transactions(transactions_ids):
    if not transactions_ids:
        return

    await db.transaction(_remove_transactions, {'transactions_ids': transactions_ids})


async def _remove_transactions(execute, arguments):
    transactions_ids = arguments['transactions_ids']

    await execute('DELETE FROM transactions WHERE id IN %(ids)s', {'ids': tuple(transactions_ids)})
    await execute('DELETE FROM operations WHERE transaction IN %(ids)s', {'ids': tuple(transactions_ids)})


async def rollback_hanged_transactions():

    results = await db.sql('SELECT id FROM transactions WHERE state=%(state)s AND created_at + lifetime < NOW()',
                           {'state': relations.TRANSACTION_STATE.OPENED.value})

    logging.info('found %s outdated transactions', len(results))

    for row in results:
        try:
            logger = log.ContextLogger()
            await rollback_transaction(row['id'], logger=logger)
        except exceptions.NoTransactionToRollback:
            continue

    logging.info('all outdated transactions rolledback')


async def remove_old_transactions(timeout):

    logging.info('try to remove old transactions')

    results = await db.sql('SELECT id FROM transactions WHERE state<>%(state)s AND created_at + %(timeout)s < NOW()',
                           {'state': relations.TRANSACTION_STATE.OPENED.value,
                            'timeout': datetime.timedelta(seconds=timeout)})

    await remove_transactions(transactions_ids=[row['id'] for row in results])

    logging.info('old transaction removed: %s', len(results))


async def clean_database():
    await db.sql('TRUNCATE operations, transactions, accounts')
