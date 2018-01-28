import datetime

from aiohttp import test_utils

from tt_protocol.protocol import bank_pb2

from tt_web import postgresql as db

from .. import relations

from . import helpers


TEST_OPERATIONS = [bank_pb2.Operation(account_id=666, currency=1, amount=-1000, type='x.1', description='y.1'),
                   bank_pb2.Operation(account_id=667, currency=1, amount=300, type='x.2', description='y.2'),
                   bank_pb2.Operation(account_id=666, currency=1, amount=500, type='x.3', description='y.3'),
                   bank_pb2.Operation(account_id=667, currency=1, amount=-100, type='x.4', description='y.4')]


async def load_operations():
    results = await db.sql('SELECT * FROM operations ORDER BY created_at ASC')

    return [bank_pb2.Operation(account_id=row['account'],
                               currency=row['currency'],
                               amount=row['amount'],
                               type=row['type'],
                               description=row['description']) for row in results]


class Base(helpers.BaseTests):

    async def check_balance(self, account_id, expected_balance):
        request = await self.client.post('/accounts/balance', data=bank_pb2.AccountBalanceRequest(account_id=account_id).SerializeToString())
        answer = await self.check_success(request, bank_pb2.AccountBalanceResponse)
        self.assertEqual(answer.balance, expected_balance)


class AccountBalanceTests(Base):

    @test_utils.unittest_run_loop
    async def test_no_balance(self):
        await self.check_balance(account_id=666, expected_balance={})

    @test_utils.unittest_run_loop
    async def test_has_record(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=101)
        await self.check_balance(account_id=666, expected_balance={1: 101})

    @test_utils.unittest_run_loop
    async def test_multiple_currencies(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=101)
        await helpers.call_change_balance(account_id=666, currency=2, amount=13)
        await self.check_balance(account_id=666, expected_balance={1: 101, 2: 13})


class AccountHistoryTests(Base):

    @test_utils.unittest_run_loop
    async def test_no_history(self):
        request = await self.client.post('/accounts/history', data=bank_pb2.AccountHistoryRequest(account_id=666).SerializeToString())
        answer = await self.check_success(request, bank_pb2.AccountHistoryResponse)

        self.assertEqual(list(answer.history), [])

    async def apply_operations(self, test_operations):
        request = await self.client.post('/transactions/start', data=bank_pb2.StartTransactionRequest(operations=test_operations,
                                                                                                      lifetime=0).SerializeToString())
        answer = await self.check_success(request, bank_pb2.StartTransactionResponse)

        await self.client.post('/transactions/commit', data=bank_pb2.CommitTransactionRequest(transaction_id=answer.transaction_id).SerializeToString())

    @test_utils.unittest_run_loop
    async def test_has_records(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)

        await self.apply_operations([bank_pb2.Operation(account_id=666, currency=1, amount=1000, type='x.1', description='y.1'),
                                     bank_pb2.Operation(account_id=666, currency=1, amount=-300, type='x.2', description='y.2')])

        await self.apply_operations([bank_pb2.Operation(account_id=667, currency=1, amount=50, type='x.3', description='y.3'),
                                     bank_pb2.Operation(account_id=666, currency=1, amount=-1, type='x.4', description='y.4')])

        request = await self.client.post('/accounts/history', data=bank_pb2.AccountHistoryRequest(account_id=666).SerializeToString())
        answer = await self.check_success(request, bank_pb2.AccountHistoryResponse)

        self.assertEqual([(record.amount, record.description) for record in answer.history],
                         [(1000, 'y.1'),
                          (-300, 'y.2'),
                          (-1, 'y.4')])

    @test_utils.unittest_run_loop
    async def test_multiple_currencies(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)

        await self.apply_operations([bank_pb2.Operation(account_id=666, currency=1, amount=1000, type='x.1', description='y.1'),
                                     bank_pb2.Operation(account_id=666, currency=1, amount=-300, type='x.2', description='y.2')])

        await self.apply_operations([bank_pb2.Operation(account_id=667, currency=1, amount=50, type='x.3', description='y.3'),
                                     bank_pb2.Operation(account_id=666, currency=2, amount=1, type='x.4', description='y.4')])

        request = await self.client.post('/accounts/history', data=bank_pb2.AccountHistoryRequest(account_id=666).SerializeToString())
        answer = await self.check_success(request, bank_pb2.AccountHistoryResponse)

        self.assertEqual([(record.currency, record.amount, record.description) for record in answer.history],
                         [(1, 1000, 'y.1'),
                          (1, -300, 'y.2'),
                          (2, 1, 'y.4')])


class StartTransactionTests(Base):

    @test_utils.unittest_run_loop
    async def test_no_operations(self):
        request = await self.client.post('/transactions/start', data=bank_pb2.StartTransactionRequest(operations=[],
                                                                                                      lifetime=0).SerializeToString())
        await self.check_error(request, error='bank.start_transaction.no_operations_specified')

    @test_utils.unittest_run_loop
    async def test_started(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=1000)

        lifetime = datetime.timedelta(seconds=100)

        request = await self.client.post('/transactions/start', data=bank_pb2.StartTransactionRequest(operations=TEST_OPERATIONS,
                                                                                                      lifetime=100).SerializeToString())
        answer = await self.check_success(request, bank_pb2.StartTransactionResponse)

        results = await db.sql('SELECT * FROM transactions WHERE id=%(id)s', {'id': answer.transaction_id})

        self.assertEqual(results[0]['state'], relations.TRANSACTION_STATE.OPENED.value)
        self.assertEqual(results[0]['lifetime'], lifetime)

        results = await db.sql('SELECT transaction FROM operations')

        loaded_operations = await load_operations()

        self.assertEqual(TEST_OPERATIONS, loaded_operations)

        # only withdraws applied on transaction start
        await self.check_balance(account_id=666, expected_balance={1: 0})
        await self.check_balance(account_id=667, expected_balance={1: 900})

    @test_utils.unittest_run_loop
    async def test_small_balance(self):
        request = await self.client.post('/transactions/start', data=bank_pb2.StartTransactionRequest(operations=TEST_OPERATIONS,
                                                                                                      lifetime=0).SerializeToString())
        await self.check_error(request, error='bank.start_transaction.no_enough_currency')

        results = await db.sql('SELECT * FROM transactions')
        self.assertEqual(results, [])

        results = await db.sql('SELECT * FROM operations ORDER BY created_at ASC')
        self.assertEqual(results, [])

        await self.check_balance(account_id=666, expected_balance={})
        await self.check_balance(account_id=667, expected_balance={})


class RollbackTransactionTests(Base):

    @test_utils.unittest_run_loop
    async def test_rollback(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=1000)

        request = await self.client.post('/transactions/start', data=bank_pb2.StartTransactionRequest(operations=TEST_OPERATIONS,
                                                                                                      lifetime=100).SerializeToString())
        answer = await self.check_success(request, bank_pb2.StartTransactionResponse)

        request = await self.client.post('/transactions/rollback', data=bank_pb2.RollbackTransactionRequest(transaction_id=answer.transaction_id).SerializeToString())
        answer = await self.check_success(request, bank_pb2.StartTransactionResponse)

        results = await db.sql('SELECT * FROM transactions')
        self.assertEqual(results[0]['state'], relations.TRANSACTION_STATE.ROLLBACKED.value)

        results = await db.sql('SELECT * FROM operations ORDER BY created_at ASC')
        self.assertEqual(results, [])

        await self.check_balance(account_id=666, expected_balance={1: 1000})
        await self.check_balance(account_id=667, expected_balance={1: 1000})

    @test_utils.unittest_run_loop
    async def test_no_transaction_to_rollback(self):
        request = await self.client.post('/transactions/rollback', data=bank_pb2.RollbackTransactionRequest(transaction_id=666).SerializeToString())
        await self.check_error(request, error='bank.rollback_transaction.no_transacton_to_rollback')


class CommitTransactionTests(Base):

    @test_utils.unittest_run_loop
    async def test_commit(self):
        await helpers.call_change_balance(account_id=666, currency=1, amount=1000)
        await helpers.call_change_balance(account_id=667, currency=1, amount=1000)

        lifetime = datetime.timedelta(seconds=100)

        request = await self.client.post('/transactions/start', data=bank_pb2.StartTransactionRequest(operations=TEST_OPERATIONS,
                                                                                                      lifetime=100).SerializeToString())
        answer = await self.check_success(request, bank_pb2.StartTransactionResponse)

        request = await self.client.post('/transactions/commit', data=bank_pb2.CommitTransactionRequest(transaction_id=answer.transaction_id).SerializeToString())
        answer = await self.check_success(request, bank_pb2.CommitTransactionResponse)

        results = await db.sql('SELECT * FROM transactions')

        self.assertEqual(results[0]['state'], relations.TRANSACTION_STATE.COMMITED.value)
        self.assertEqual(results[0]['lifetime'], lifetime)

        loaded_operations = await load_operations()
        self.assertEqual(TEST_OPERATIONS, loaded_operations)

        # only withdraws applied on transaction start
        await self.check_balance(account_id=666, expected_balance={1: 500})
        await self.check_balance(account_id=667, expected_balance={1: 1200})

    @test_utils.unittest_run_loop
    async def test_no_transaction_to_commit(self):
        request = await self.client.post('/transactions/commit', data=bank_pb2.CommitTransactionRequest(transaction_id=666).SerializeToString())
        await self.check_error(request, error='bank.commit_transaction.no_transacton_to_commit')
