import random
import datetime

from aiohttp import test_utils

from tt_web import postgresql as db

from .. import objects
from .. import relations
from .. import operations
from .. import exceptions

from . import helpers


TEST_OPERATIONS = [objects.Operation(account_id=666, currency=1, amount=-1000, type='x.1', description='y.1'),
                   objects.Operation(account_id=667, currency=1, amount=300, type='x.2', description='y.2'),
                   objects.Operation(account_id=666, currency=1, amount=500, type='x.3', description='y.3'),
                   objects.Operation(account_id=667, currency=1, amount=-100, type='x.4', description='y.4')]


async def load_operations():
    results = await db.sql('SELECT * FROM operations ORDER BY created_at ASC')

    return [objects.Operation(account_id=row['account'],
                              currency=row['currency'],
                              amount=row['amount'],
                              type=row['type'],
                              description=row['description']) for row in results]


class Base(helpers.BaseTests):

    async def check_balance(self, account_id, expected_balance):
        balance = await operations.load_balance(account_id=account_id)
        self.assertEqual(expected_balance, balance)


class LoadBalanceTests(Base):

    @test_utils.unittest_run_loop
    async def test_no_record(self):
        await self.check_balance(account_id=666, expected_balance={})

    @test_utils.unittest_run_loop
    async def test_has_record(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=100500)
        await self.check_balance(account_id=666, expected_balance={1: 100500})

    @test_utils.unittest_run_loop
    async def test_multiple_currencies(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=100500)
        await helpers.call_change_balance(account_id=666, currency=2, amount=1)
        await helpers.call_change_balance(account_id=666, currency=3, amount=13)
        await self.check_balance(account_id=666, expected_balance={1: 100500,
                                                                   2: 1,
                                                                   3: 13})

    @test_utils.unittest_run_loop
    async def test_zero_amount(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=0)
        await self.check_balance(account_id=666, expected_balance={1: 0})

    @test_utils.unittest_run_loop
    async def test_multiple_accounts(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=100500)
        await helpers.call_change_balance(account_id=667, currency=2, amount=1)
        await helpers.call_change_balance(account_id=666, currency=3, amount=13)

        await self.check_balance(account_id=666, expected_balance={1: 100500,
                                                                   3: 13})

        await self.check_balance(account_id=667, expected_balance={2: 1})


class LoadHistoryTests(Base):

    @test_utils.unittest_run_loop
    async def test_no_records(self):
        history = await operations.load_history(account_id=666)
        self.assertEqual(history, [])

    @test_utils.unittest_run_loop
    async def test_has_records(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)

        await operations.start_transaction(operations=[objects.Operation(account_id=666,
                                                                         currency=1,
                                                                         amount=1000,
                                                                         type='x.1',
                                                                         description='y.1'),
                                                       objects.Operation(account_id=666,
                                                                         currency=1,
                                                                         amount=-300,
                                                                         type='x.2',
                                                                         description='y.2')],
                                           lifetime=datetime.timedelta(),
                                           restrictions=objects.Restrictions(),
                                           logger=helpers.TEST_LOGGER,
                                           autocommit=True)

        await operations.start_transaction(operations=[objects.Operation(account_id=667,
                                                                         currency=1,
                                                                         amount=50,
                                                                         type='x.3',
                                                                         description='y.3'),
                                                       objects.Operation(account_id=666,
                                                                         currency=1,
                                                                         amount=-1,
                                                                         type='x.4',
                                                                         description='y.4')],
                                           lifetime=datetime.timedelta(),
                                           restrictions=objects.Restrictions(),
                                           logger=helpers.TEST_LOGGER,
                                           autocommit=True)

        history = await operations.load_history(account_id=666)

        self.assertEqual([(record.amount, record.description) for record in history],
                         [(1000, 'y.1'),
                          (-300, 'y.2'),
                          (-1, 'y.4')])


class StartTransactionTests(Base):

    @test_utils.unittest_run_loop
    async def test_no_operations(self):
        with self.assertRaises(exceptions.NoOperationsInTransaction):
            await operations.start_transaction(operations=[],
                                               lifetime=datetime.timedelta(),
                                               restrictions=objects.Restrictions(),
                                               logger=helpers.TEST_LOGGER,
                                               autocommit=False)

    @test_utils.unittest_run_loop
    async def test_started(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=1000)

        lifetime = datetime.timedelta(seconds=100)

        transaction_id = await operations.start_transaction(operations=TEST_OPERATIONS,
                                                            lifetime=lifetime,
                                                            logger=helpers.TEST_LOGGER,
                                                            restrictions=objects.Restrictions(),
                                                            autocommit=False)

        results = await db.sql('SELECT * FROM transactions WHERE id=%(id)s', {'id': transaction_id})

        self.assertEqual(results[0]['state'], relations.TRANSACTION_STATE.OPENED.value)
        self.assertEqual(results[0]['lifetime'], lifetime)

        results = await db.sql('SELECT transaction FROM operations')

        for row in results:
            self.assertEqual(transaction_id, row['transaction'])

        loaded_operations = await load_operations()

        self.assertEqual(TEST_OPERATIONS, loaded_operations)

        # only withdraws applied on transaction start
        await self.check_balance(account_id=666, expected_balance={1: 0})
        await self.check_balance(account_id=667, expected_balance={1: 900})

    @test_utils.unittest_run_loop
    async def test_small_balance__hard_minimum(self):
        with self.assertRaises(exceptions.BalanceChangeExceededRestrictions):
            await operations.start_transaction(operations=TEST_OPERATIONS,
                                               lifetime=datetime.timedelta(seconds=100),
                                               restrictions=objects.Restrictions(),
                                               logger=helpers.TEST_LOGGER,
                                               autocommit=False)

        results = await db.sql('SELECT * FROM transactions')

        self.assertEqual(results, [])

        results = await db.sql('SELECT * FROM operations ORDER BY created_at ASC')

        self.assertEqual(results, [])

        await self.check_balance(account_id=666, expected_balance={})
        await self.check_balance(account_id=667, expected_balance={})

    @test_utils.unittest_run_loop
    async def test_small_balance__not_restricted(self):

        lifetime = datetime.timedelta(seconds=100)

        transaction_id = await operations.start_transaction(operations=TEST_OPERATIONS,
                                                            lifetime=lifetime,
                                                            restrictions=objects.Restrictions(hard_minimum=-100000),
                                                            logger=helpers.TEST_LOGGER,
                                                            autocommit=False)

        results = await db.sql('SELECT * FROM transactions')

        self.assertEqual(results[0]['state'], relations.TRANSACTION_STATE.OPENED.value)
        self.assertEqual(results[0]['lifetime'], lifetime)

        results = await db.sql('SELECT * FROM operations ORDER BY created_at ASC')

        for row in results:
            self.assertEqual(transaction_id, row['transaction'])

        loaded_operations = await load_operations()

        self.assertEqual(TEST_OPERATIONS, loaded_operations)

        await self.check_balance(account_id=666, expected_balance={1: -1000})
        await self.check_balance(account_id=667, expected_balance={1: -100})

    @test_utils.unittest_run_loop
    async def test_small_balance__soft_minimum(self):

        lifetime = datetime.timedelta(seconds=100)

        transaction_id = await operations.start_transaction(operations=TEST_OPERATIONS,
                                                            lifetime=lifetime,
                                                            restrictions=objects.Restrictions(hard_minimum=None,
                                                                                              soft_minimum=-500),
                                                            logger=helpers.TEST_LOGGER,
                                                            autocommit=False)

        results = await db.sql('SELECT * FROM transactions')

        self.assertEqual(results[0]['state'], relations.TRANSACTION_STATE.OPENED.value)
        self.assertEqual(results[0]['lifetime'], lifetime)

        results = await db.sql('SELECT * FROM operations ORDER BY created_at ASC')

        for row in results:
            self.assertEqual(transaction_id, row['transaction'])

        loaded_operations = await load_operations()

        self.assertEqual(TEST_OPERATIONS, loaded_operations)

        await self.check_balance(account_id=666, expected_balance={1: -500})
        await self.check_balance(account_id=667, expected_balance={1: -100})

    @test_utils.unittest_run_loop
    async def test_large_balance__hard_maximum(self):
        with self.assertRaises(exceptions.BalanceChangeExceededRestrictions):
            await operations.start_transaction(operations=TEST_OPERATIONS,
                                               lifetime=datetime.timedelta(seconds=100),
                                               restrictions=objects.Restrictions(hard_minimum=None,
                                                                                 hard_maximum=1),
                                               logger=helpers.TEST_LOGGER,
                                               autocommit=True)

        await self.check_balance(account_id=666, expected_balance={})
        await self.check_balance(account_id=667, expected_balance={})

    @test_utils.unittest_run_loop
    async def test_large_balance__not_restricted(self):

        lifetime = datetime.timedelta(seconds=100)

        await operations.start_transaction(operations=TEST_OPERATIONS,
                                           lifetime=lifetime,
                                           restrictions=objects.Restrictions(hard_minimum=None),
                                           logger=helpers.TEST_LOGGER,
                                           autocommit=True)

        await self.check_balance(account_id=666, expected_balance={1: -500})
        await self.check_balance(account_id=667, expected_balance={1: 200})

    @test_utils.unittest_run_loop
    async def test_large_balance__soft_maximum(self):

        lifetime = datetime.timedelta(seconds=100)

        await operations.start_transaction(operations=TEST_OPERATIONS,
                                           lifetime=lifetime,
                                           restrictions=objects.Restrictions(hard_minimum=None,
                                                                             soft_maximum=133),
                                           logger=helpers.TEST_LOGGER,
                                           autocommit=True)

        await self.check_balance(account_id=666, expected_balance={1: -500})
        await self.check_balance(account_id=667, expected_balance={1: 133})

    @test_utils.unittest_run_loop
    async def test_no_balance_record(self):
        test_operations = [objects.Operation(account_id=666, currency=1, amount=500, type='x.1', description='y.1')]

        lifetime = datetime.timedelta(seconds=100)

        transaction_id = await operations.start_transaction(operations=test_operations,
                                                            lifetime=lifetime,
                                                            restrictions=objects.Restrictions(),
                                                            logger=helpers.TEST_LOGGER,
                                                            autocommit=False)

        results = await db.sql('SELECT * FROM transactions WHERE id=%(id)s', {'id': transaction_id})

        self.assertEqual(results[0]['state'], relations.TRANSACTION_STATE.OPENED.value)
        self.assertEqual(results[0]['lifetime'], lifetime)

        loaded_operations = await load_operations()

        self.assertEqual(test_operations, loaded_operations)

        await self.check_balance(account_id=666, expected_balance={})

    @test_utils.unittest_run_loop
    async def test_autocommit(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=1000)

        lifetime = datetime.timedelta(seconds=100)

        transaction_id = await operations.start_transaction(operations=TEST_OPERATIONS,
                                                            lifetime=lifetime,
                                                            restrictions=objects.Restrictions(),
                                                            logger=helpers.TEST_LOGGER,
                                                            autocommit=True)

        results = await db.sql('SELECT * FROM transactions WHERE id=%(id)s', {'id': transaction_id})

        self.assertEqual(results[0]['state'], relations.TRANSACTION_STATE.COMMITED.value)
        self.assertEqual(results[0]['lifetime'], lifetime)

        loaded_operations = await load_operations()

        self.assertEqual(TEST_OPERATIONS, loaded_operations)

        # only withdraws applied on transaction start
        await self.check_balance(account_id=666, expected_balance={1: 500})
        await self.check_balance(account_id=667, expected_balance={1: 1200})

    @test_utils.unittest_run_loop
    async def test_restrictions_saved(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=1000)

        lifetime = datetime.timedelta(seconds=100)

        restrictions = objects.Restrictions(hard_minimum=0,
                                            hard_maximum=100000,
                                            soft_minimum=-10000,
                                            soft_maximum=30000)

        transaction_id = await operations.start_transaction(operations=TEST_OPERATIONS,
                                                            lifetime=lifetime,
                                                            logger=helpers.TEST_LOGGER,
                                                            restrictions=restrictions,
                                                            autocommit=False)

        results = await db.sql('SELECT * FROM transactions WHERE id=%(id)s', {'id': transaction_id})

        self.assertEqual(results[0]['data']['restrictions'], restrictions.serialize())


class ChangeBalanceTests(Base):

    @test_utils.unittest_run_loop
    async def test_no_record(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=100500)
        await self.check_balance(account_id=666, expected_balance={1: 100500})

    @test_utils.unittest_run_loop
    async def test_no_record__withdraw(self):
        with self.assertRaises(exceptions.BalanceChangeExceededRestrictions):
            await helpers.call_change_balance(account_id=666, currency=1, amount=-100500)

        await self.check_balance(account_id=666, expected_balance={1: 0})

    @test_utils.unittest_run_loop
    async def test_has_record(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=100500)
        await helpers.call_change_balance(account_id=666, currency=1, amount=1)

        await self.check_balance(account_id=666, expected_balance={1: 100501})

    @test_utils.unittest_run_loop
    async def test_has_record__withdraw(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=100500)
        await helpers.call_change_balance(account_id=666, currency=1, amount=-1)

        await self.check_balance(account_id=666, expected_balance={1: 100499})

    @test_utils.unittest_run_loop
    async def test_has_record__withdraw_too_match(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=100500)

        with self.assertRaises(exceptions.BalanceChangeExceededRestrictions):
            await helpers.call_change_balance(account_id=666, currency=1, amount=-100501)

        await self.check_balance(account_id=666, expected_balance={1: 100500})

    @test_utils.unittest_run_loop
    async def test_multiple_currencies(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=100500)
        await helpers.call_change_balance(account_id=666, currency=2, amount=1000)
        await helpers.call_change_balance(account_id=666, currency=3, amount=14)
        await helpers.call_change_balance(account_id=666, currency=2, amount=-10)
        await helpers.call_change_balance(account_id=666, currency=1, amount=-14)

        await self.check_balance(account_id=666, expected_balance={1: 100486,
                                                                   2: 990,
                                                                   3: 14})

    @test_utils.unittest_run_loop
    async def test_withdraw_error_when_has_another_currency(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=100500)

        with self.assertRaises(exceptions.BalanceChangeExceededRestrictions):
            await helpers.call_change_balance(account_id=666, currency=2, amount=-10)


class RollbackTransactionTests(Base):

    @test_utils.unittest_run_loop
    async def test_no_transaction(self):
        with self.assertRaises(exceptions.NoTransactionToRollback):
            await operations.rollback_transaction(transaction_id=666, logger=helpers.TEST_LOGGER)

    @test_utils.unittest_run_loop
    async def test_wrong_state(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=1000)

        lifetime = datetime.timedelta(seconds=100)

        transaction_id = await operations.start_transaction(operations=TEST_OPERATIONS,
                                                            lifetime=lifetime,
                                                            restrictions=objects.Restrictions(),
                                                            logger=helpers.TEST_LOGGER,
                                                            autocommit=False)

        await db.sql('UPDATE transactions SET state=%(state)s',
                     {'state': random.choice((relations.TRANSACTION_STATE.COMMITED.value,
                                              relations.TRANSACTION_STATE.ROLLBACKED.value))})

        with self.assertRaises(exceptions.NoTransactionToRollback):
            await operations.rollback_transaction(transaction_id=transaction_id, logger=helpers.TEST_LOGGER)

    @test_utils.unittest_run_loop
    async def test_rollback(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=1000)

        lifetime = datetime.timedelta(seconds=100)

        transaction_id = await operations.start_transaction(operations=TEST_OPERATIONS,
                                                            lifetime=lifetime,
                                                            restrictions=objects.Restrictions(),
                                                            logger=helpers.TEST_LOGGER,
                                                            autocommit=False)

        await operations.rollback_transaction(transaction_id, logger=helpers.TEST_LOGGER)

        results = await db.sql('SELECT * FROM transactions WHERE id=%(id)s', {'id': transaction_id})

        self.assertEqual(results[0]['state'], relations.TRANSACTION_STATE.ROLLBACKED.value)

        results = await db.sql('SELECT * FROM operations ORDER BY created_at ASC')

        self.assertEqual(results, [])

        # rollback amoutns
        await self.check_balance(account_id=666, expected_balance={1: 1000})
        await self.check_balance(account_id=667, expected_balance={1: 1000})

    @test_utils.unittest_run_loop
    async def test_rollback_only_one_transaction(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=1000)

        lifetime = datetime.timedelta(seconds=100)

        test_operations_1 = TEST_OPERATIONS

        test_operations_2 = [objects.Operation(account_id=667, currency=1, amount=-1, type='x.5', description='y.5')]

        test_operations_3 = [objects.Operation(account_id=666, currency=1, amount=1, type='x.6', description='y.6')]

        transaction_1_id = await operations.start_transaction(operations=test_operations_1,
                                                              lifetime=lifetime,
                                                              restrictions=objects.Restrictions(),
                                                              logger=helpers.TEST_LOGGER,
                                                              autocommit=False)

        transaction_2_id = await operations.start_transaction(operations=test_operations_2,
                                                              lifetime=lifetime,
                                                              restrictions=objects.Restrictions(),
                                                              logger=helpers.TEST_LOGGER,
                                                              autocommit=False)

        transaction_3_id = await operations.start_transaction(operations=test_operations_3,
                                                              lifetime=lifetime,
                                                              restrictions=objects.Restrictions(),
                                                              logger=helpers.TEST_LOGGER,
                                                              autocommit=False)

        await operations.rollback_transaction(transaction_1_id, logger=helpers.TEST_LOGGER)
        await operations.commit_transaction(transaction_3_id, logger=helpers.TEST_LOGGER)

        results = await db.sql('SELECT * FROM transactions ORDER BY created_at ASC')
        self.assertEqual(results[0]['state'], relations.TRANSACTION_STATE.ROLLBACKED.value)
        self.assertEqual(results[1]['state'], relations.TRANSACTION_STATE.OPENED.value)
        self.assertEqual(results[2]['state'], relations.TRANSACTION_STATE.COMMITED.value)

        loaded_operations = await load_operations()

        self.assertEqual(loaded_operations, [test_operations_2[0],
                                             test_operations_3[0]])

        # rollback amoutns
        await self.check_balance(account_id=666, expected_balance={1: 1001})
        await self.check_balance(account_id=667, expected_balance={1: 999})


class CommitTransactionTests(Base):

    @test_utils.unittest_run_loop
    async def test_no_transaction(self):
        with self.assertRaises(exceptions.NoTransactionToCommit):
            await operations.commit_transaction(transaction_id=666, logger=helpers.TEST_LOGGER)

    @test_utils.unittest_run_loop
    async def test_wrong_state(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=1000)

        lifetime = datetime.timedelta(seconds=100)

        transaction_id = await operations.start_transaction(operations=TEST_OPERATIONS,
                                                            lifetime=lifetime,
                                                            restrictions=objects.Restrictions(),
                                                            logger=helpers.TEST_LOGGER,
                                                            autocommit=False)

        await db.sql('UPDATE transactions SET state=%(state)s',
                     {'state': random.choice((relations.TRANSACTION_STATE.COMMITED.value,
                                              relations.TRANSACTION_STATE.ROLLBACKED.value))})

        with self.assertRaises(exceptions.NoTransactionToCommit):
            await operations.commit_transaction(transaction_id=transaction_id, logger=helpers.TEST_LOGGER)

    @test_utils.unittest_run_loop
    async def test_commit(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=1000)

        lifetime = datetime.timedelta(seconds=100)

        transaction_id = await operations.start_transaction(operations=TEST_OPERATIONS,
                                                            lifetime=lifetime,
                                                            restrictions=objects.Restrictions(),
                                                            logger=helpers.TEST_LOGGER,
                                                            autocommit=False)

        await operations.commit_transaction(transaction_id, logger=helpers.TEST_LOGGER)

        results = await db.sql('SELECT * FROM transactions WHERE id=%(id)s', {'id': transaction_id})

        self.assertEqual(results[0]['state'], relations.TRANSACTION_STATE.COMMITED.value)
        self.assertEqual(results[0]['lifetime'], lifetime)

        loaded_operations = await load_operations()

        self.assertEqual(TEST_OPERATIONS, loaded_operations)

        # only withdraws applied on transaction start
        await self.check_balance(account_id=666, expected_balance={1: 500})
        await self.check_balance(account_id=667, expected_balance={1: 1200})

    @test_utils.unittest_run_loop
    async def test_commit_only_specified_transaction(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=1000)

        lifetime = datetime.timedelta(seconds=100)

        test_operations_1 = TEST_OPERATIONS

        test_operations_2 = [objects.Operation(account_id=667, currency=1, amount=-1, type='x.5', description='y.5')]

        test_operations_3 = [objects.Operation(account_id=666, currency=1, amount=1, type='x.6', description='y.6')]

        transaction_1_id = await operations.start_transaction(operations=test_operations_1,
                                                              lifetime=lifetime,
                                                              restrictions=objects.Restrictions(),
                                                              logger=helpers.TEST_LOGGER,
                                                              autocommit=False)

        transaction_2_id = await operations.start_transaction(operations=test_operations_2,
                                                              lifetime=lifetime,
                                                              restrictions=objects.Restrictions(),
                                                              logger=helpers.TEST_LOGGER,
                                                              autocommit=False)

        transaction_3_id = await operations.start_transaction(operations=test_operations_3,
                                                              lifetime=lifetime,
                                                              restrictions=objects.Restrictions(),
                                                              logger=helpers.TEST_LOGGER,
                                                              autocommit=False)

        await operations.rollback_transaction(transaction_3_id, logger=helpers.TEST_LOGGER)
        await operations.commit_transaction(transaction_1_id, logger=helpers.TEST_LOGGER)

        results = await db.sql('SELECT * FROM transactions ORDER BY created_at ASC')
        self.assertEqual(results[0]['state'], relations.TRANSACTION_STATE.COMMITED.value)
        self.assertEqual(results[1]['state'], relations.TRANSACTION_STATE.OPENED.value)
        self.assertEqual(results[2]['state'], relations.TRANSACTION_STATE.ROLLBACKED.value)

        loaded_operations = await load_operations()

        self.assertEqual(loaded_operations, test_operations_1 + test_operations_2)

        # only withdraws applied on transaction start
        await self.check_balance(account_id=666, expected_balance={1: 500})
        await self.check_balance(account_id=667, expected_balance={1: 1199})

    @test_utils.unittest_run_loop
    async def test_restrictions_applied(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=1000)

        lifetime = datetime.timedelta(seconds=100)

        transaction_id = await operations.start_transaction(operations=TEST_OPERATIONS,
                                                            lifetime=lifetime,
                                                            restrictions=objects.Restrictions(soft_maximum=666),
                                                            logger=helpers.TEST_LOGGER,
                                                            autocommit=False)

        await operations.commit_transaction(transaction_id, logger=helpers.TEST_LOGGER)

        results = await db.sql('SELECT * FROM transactions WHERE id=%(id)s', {'id': transaction_id})

        self.assertEqual(results[0]['state'], relations.TRANSACTION_STATE.COMMITED.value)
        self.assertEqual(results[0]['lifetime'], lifetime)

        loaded_operations = await load_operations()

        self.assertEqual(TEST_OPERATIONS, loaded_operations)

        # only withdraws applied on transaction start
        await self.check_balance(account_id=666, expected_balance={1: 500})
        await self.check_balance(account_id=667, expected_balance={1: 666})


class RollbackHangedTransactionsTests(Base):

    @test_utils.unittest_run_loop
    async def test_no_transactions(self):
        await operations.rollback_hanged_transactions()

    @test_utils.unittest_run_loop
    async def test_lifetime(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=1000)

        await operations.start_transaction(operations=[objects.Operation(account_id=666,
                                                                         currency=1,
                                                                         amount=-1,
                                                                         type='x.1',
                                                                         description='y.1')],
                                           lifetime=datetime.timedelta(seconds=100),
                                           restrictions=objects.Restrictions(),
                                           logger=helpers.TEST_LOGGER,
                                           autocommit=False)

        await operations.start_transaction(operations=[objects.Operation(account_id=667,
                                                                         currency=1,
                                                                         amount=-10,
                                                                         type='x.2',
                                                                         description='y.2')],
                                           lifetime=datetime.timedelta(seconds=0),
                                           restrictions=objects.Restrictions(),
                                           logger=helpers.TEST_LOGGER,
                                           autocommit=False)

        await operations.rollback_hanged_transactions()

        results = await db.sql('SELECT * FROM transactions ORDER BY created_at')

        self.assertEqual(results[0]['state'], relations.TRANSACTION_STATE.OPENED.value)
        self.assertEqual(results[1]['state'], relations.TRANSACTION_STATE.ROLLBACKED.value)

        await self.check_balance(account_id=666, expected_balance={1: 999})
        await self.check_balance(account_id=667, expected_balance={1: 1000})

    @test_utils.unittest_run_loop
    async def test_state(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=668, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=669, currency=1, amount=1000)

        transaction_1_id = await operations.start_transaction(operations=[objects.Operation(account_id=666,
                                                                                            currency=1,
                                                                                            amount=-1,
                                                                                            type='x.1',
                                                                                            description='y.1')],
                                                              lifetime=datetime.timedelta(seconds=0),
                                                              restrictions=objects.Restrictions(),
                                                              logger=helpers.TEST_LOGGER,
                                                              autocommit=False)

        transaction_2_id = await operations.start_transaction(operations=[objects.Operation(account_id=667,
                                                                                            currency=1,
                                                                                            amount=-10,
                                                                                            type='x.2',
                                                                                            description='y.2')],
                                                              lifetime=datetime.timedelta(seconds=0),
                                                              restrictions=objects.Restrictions(),
                                                              logger=helpers.TEST_LOGGER,
                                                              autocommit=False)

        transaction_3_id = await operations.start_transaction(operations=[objects.Operation(account_id=668,
                                                                                            currency=1,
                                                                                            amount=-100,
                                                                                            type='x.3',
                                                                                            description='y.3')],
                                                              lifetime=datetime.timedelta(seconds=0),
                                                              restrictions=objects.Restrictions(),
                                                              logger=helpers.TEST_LOGGER,
                                                              autocommit=False)

        transaction_4_id = await operations.start_transaction(operations=[objects.Operation(account_id=669,
                                                                                            currency=1,
                                                                                            amount=-10,
                                                                                            type='x.4',
                                                                                            description='y.4')],
                                                              lifetime=datetime.timedelta(seconds=0),
                                                              restrictions=objects.Restrictions(),
                                                              logger=helpers.TEST_LOGGER,
                                                              autocommit=False)

        await operations.rollback_transaction(transaction_id=transaction_3_id, logger=helpers.TEST_LOGGER)
        await operations.commit_transaction(transaction_id=transaction_1_id, logger=helpers.TEST_LOGGER)

        await operations.rollback_hanged_transactions()

        results = await db.sql('SELECT * FROM transactions ORDER BY created_at')

        self.assertEqual(results[0]['state'], relations.TRANSACTION_STATE.COMMITED.value)
        self.assertEqual(results[1]['state'], relations.TRANSACTION_STATE.ROLLBACKED.value)
        self.assertEqual(results[2]['state'], relations.TRANSACTION_STATE.ROLLBACKED.value)
        self.assertEqual(results[3]['state'], relations.TRANSACTION_STATE.ROLLBACKED.value)

        await self.check_balance(account_id=666, expected_balance={1: 999})
        await self.check_balance(account_id=667, expected_balance={1: 1000})
        await self.check_balance(account_id=668, expected_balance={1: 1000})


class MultipleCurrenciesTransactionsTests(Base):

    TEST_OPERATIONS = [objects.Operation(account_id=666, currency=1, amount=-1000, type='x.1', description='y.1'),
                       objects.Operation(account_id=667, currency=2, amount=300, type='x.2', description='y.2'),
                       objects.Operation(account_id=666, currency=1, amount=500, type='x.3', description='y.3'),
                       objects.Operation(account_id=667, currency=2, amount=-100, type='x.4', description='y.4'),

                       objects.Operation(account_id=666, currency=3, amount=-100, type='x.5', description='y.5'),
                       objects.Operation(account_id=667, currency=1, amount=30, type='x.6', description='y.6'),
                       objects.Operation(account_id=666, currency=3, amount=50, type='x.7', description='y.7'),
                       objects.Operation(account_id=667, currency=1, amount=-10, type='x.8', description='y.8')]

    async def prepair(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=10000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=10000)
        await helpers.call_change_balance(account_id=666, currency=3, amount=10000)
        await helpers.call_change_balance(account_id=667, currency=2, amount=10000)

        transaction_id = await operations.start_transaction(operations=self.TEST_OPERATIONS,
                                                            lifetime=datetime.timedelta(seconds=100),
                                                            restrictions=objects.Restrictions(),
                                                            logger=helpers.TEST_LOGGER,
                                                            autocommit=False)

        return transaction_id

    @test_utils.unittest_run_loop
    async def test_start(self):
        await self.prepair()

        loaded_operations = await load_operations()

        self.assertEqual(self.TEST_OPERATIONS, loaded_operations)

        await self.check_balance(account_id=666, expected_balance={1: 9000, 3: 9900})
        await self.check_balance(account_id=667, expected_balance={1: 9990, 2: 9900})

    @test_utils.unittest_run_loop
    async def test_rollback(self):
        transaction_id = await self.prepair()

        await operations.rollback_transaction(transaction_id, logger=helpers.TEST_LOGGER)

        loaded_operations = await load_operations()

        self.assertEqual([], loaded_operations)

        await self.check_balance(account_id=666, expected_balance={1: 10000, 3: 10000})
        await self.check_balance(account_id=667, expected_balance={1: 10000, 2: 10000})

    @test_utils.unittest_run_loop
    async def test_start(self):
        transaction_id = await self.prepair()

        await operations.commit_transaction(transaction_id, logger=helpers.TEST_LOGGER)

        loaded_operations = await load_operations()

        self.assertEqual(self.TEST_OPERATIONS, loaded_operations)

        await self.check_balance(account_id=666, expected_balance={1: 9500, 3: 9950})
        await self.check_balance(account_id=667, expected_balance={1: 10020, 2: 10200})


class RemoveTransactionsTests(Base):

    async def prepair_data(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=668, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=669, currency=1, amount=1000)

        transactions_ids = []

        for i in range(4):
            account_id = 666 + i
            await helpers.call_change_balance(account_id=account_id, currency=1, amount=1000)
            transaction_id = await operations.start_transaction(operations=[objects.Operation(account_id=666,
                                                                                              currency=1,
                                                                                              amount=-1,
                                                                                              type='x.1',
                                                                                              description='y.1')],
                                                                lifetime=datetime.timedelta(seconds=0),
                                                                restrictions=objects.Restrictions(),
                                                                logger=helpers.TEST_LOGGER,
                                                                autocommit=False)
            transactions_ids.append(transaction_id)

        await operations.rollback_transaction(transaction_id=transactions_ids[2], logger=helpers.TEST_LOGGER)
        await operations.commit_transaction(transaction_id=transactions_ids[0], logger=helpers.TEST_LOGGER)

        return transactions_ids

    async def check_transactions_existence(self, transactions_ids):
        results = await db.sql('SELECT id FROM transactions')

        found_transactions = {row['id'] for row in results}

        self.assertEqual(found_transactions, set(transactions_ids))

    async def check_operations_existence(self, transactions_ids):
        results = await db.sql('SELECT transaction FROM operations')

        found_transactions = {row['transaction'] for row in results}

        self.assertEqual(found_transactions, set(transactions_ids))

    @test_utils.unittest_run_loop
    async def test_no_transactions(self):
        transactions_ids = await self.prepair_data()

        await operations.remove_transactions(transactions_ids=[])

        await self.check_transactions_existence(transactions_ids)
        await self.check_operations_existence([transactions_ids[0],
                                               transactions_ids[1],
                                               transactions_ids[3]])

    @test_utils.unittest_run_loop
    async def test_has_transactions(self):
        transactions_ids = await self.prepair_data()

        await operations.remove_transactions(transactions_ids=[transactions_ids[0],
                                                               transactions_ids[2],
                                                               transactions_ids[3]])

        await self.check_transactions_existence([transactions_ids[1]])
        await self.check_operations_existence([transactions_ids[1]])

    @test_utils.unittest_run_loop
    async def test_remove_old_transactions(self):
        transactions_ids = await self.prepair_data()

        for i, transaction_id in enumerate(transactions_ids):
            await db.sql('UPDATE transactions SET created_at=%(date)s WHERE id=%(id)s',
                         {'id': transaction_id,
                          'date': datetime.datetime.utcnow()-datetime.timedelta(days=i)})

        await operations.remove_old_transactions(timeout=1.5*24*60*60)

        await self.check_transactions_existence([transactions_ids[0],
                                                 transactions_ids[1],
                                                 transactions_ids[3]])
        await self.check_operations_existence([transactions_ids[0],
                                               transactions_ids[1],
                                               transactions_ids[3]])
