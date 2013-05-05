# coding: utf-8

import datetime

import mock

from common.utils import testcase

from common.postponed_tasks import POSTPONED_TASK_LOGIC_RESULT

from bank.transaction import Transaction
from bank.prototypes import InvoicePrototype, AccountPrototype as BankAccountPrototype
from bank.relations import ENTITY_TYPE, CURRENCY_TYPE, INVOICE_STATE

from game.logic import create_test_map

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from accounts.payments.postponed_tasks import BuyPremium, BUY_PREMIUM_STATE


class BuyPremiumPosponedTaskTests(testcase.TestCase):

    def setUp(self):
        super(BuyPremiumPosponedTaskTests, self).setUp()

        create_test_map()

        self.initial_amount = 500
        self.days = 13
        self.amount = 130


        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        self.bank_account = BankAccountPrototype.create(entity_type=ENTITY_TYPE.GAME_ACCOUNT,
                                                        entity_id=self.account.id,
                                                        currency=CURRENCY_TYPE.PREMIUM)
        self.bank_account.amount = self.initial_amount
        self.bank_account.save()

        self.invoice = InvoicePrototype.create(recipient_type=ENTITY_TYPE.GAME_ACCOUNT,
                                               recipient_id=self.account.id,
                                               sender_type=ENTITY_TYPE.GAME_LOGIC,
                                               sender_id=0,
                                               currency=CURRENCY_TYPE.PREMIUM,
                                               amount=-self.amount,
                                               description='transaction-description',
                                               operation_uid='transaction-operation-ui')

        self.task = BuyPremium(account_id=self.account.id,
                               days=self.days,
                               transaction=Transaction(self.invoice.id))

    def test_create(self):
        self.assertTrue(self.task.state._is_TRANSACTION_REQUESTED)
        self.assertEqual(self.task.days, self.days)

    def test_serialization(self):
        self.assertEqual(self.task.serialize(), BuyPremium.deserialize(self.task.serialize()).serialize())

    def test_process__transaction_requested__invoice_unprocessed(self):
        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.WAIT)
        self.assertTrue(self.task.state._is_TRANSACTION_REQUESTED)

        self.account.reload()
        self.assertTrue(self.account.premium_end_at < datetime.datetime.now())

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)

    def test_process__transaction_requested__invoice_rejected(self):
        self.invoice.state = INVOICE_STATE.REJECTED
        self.invoice.save()

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state._is_TRANSACTION_REJECTED)

        self.account.reload()
        self.assertTrue(self.account.premium_end_at < datetime.datetime.now())

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)

    def test_process__transaction_requested__invoice_wrong_state(self):
        self.invoice.state = INVOICE_STATE.CONFIRMED
        self.invoice.save()

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state._is_ERROR_IN_FREEZING_TRANSACTION)

        self.account.reload()
        self.assertTrue(self.account.premium_end_at < datetime.datetime.now())

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)

    def test_process__transaction_requested__invoice_frozen(self):
        self.invoice.state = INVOICE_STATE.FROZEN
        self.invoice.save()

        main_task = mock.Mock()

        self.assertEqual(self.task.process(main_task=main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)
        self.assertTrue(self.task.state._is_TRANSACTION_FROZEN)

        with mock.patch('accounts.workers.accounts_manager.Worker.cmd_task') as cmd_task:
            postsave_actions = main_task.extend_postsave_actions.call_args[0][0]
            for action in postsave_actions:
                action()

        self.assertEqual(cmd_task.call_count, 1)

        self.account.reload()
        self.assertTrue(self.account.premium_end_at < datetime.datetime.now())

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)

    def test_process__transaction_frozen(self):
        self.invoice.state = INVOICE_STATE.FROZEN
        self.invoice.save()

        self.task.state = BUY_PREMIUM_STATE.TRANSACTION_FROZEN

        with mock.patch('game.heroes.prototypes.HeroPrototype.cmd_update_with_account_data') as cmd_update_with_account_data:
            with mock.patch('bank.transaction.Transaction.confirm') as transaction_confirm:
                self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.WAIT)

        self.assertEqual(cmd_update_with_account_data.call_count, 1)
        self.assertEqual(transaction_confirm.call_count, 1)

        self.account.reload()
        self.assertTrue(self.account.premium_end_at > datetime.datetime.now())
        self.assertTrue(datetime.datetime.now() + datetime.timedelta(days=self.days-1) < self.account.premium_end_at)
        self.assertTrue(datetime.datetime.now() + datetime.timedelta(days=self.days+1) > self.account.premium_end_at)

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount) # money will be withdrawed after transaction confirm processed

    def test_process__wait_confirmation__transaction_frozen(self):
        self.invoice.state = INVOICE_STATE.FROZEN
        self.invoice.save()

        self.task.state = BUY_PREMIUM_STATE.WAIT_TRANSACTION_CONFIRMATION

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.WAIT)
        self.assertTrue(self.task.state._is_WAIT_TRANSACTION_CONFIRMATION)

    def test_process__wait_confirmation__transaction_confirmed(self):
        self.invoice.state = INVOICE_STATE.CONFIRMED
        self.invoice.save()

        self.task.state = BUY_PREMIUM_STATE.WAIT_TRANSACTION_CONFIRMATION

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertTrue(self.task.state._is_SUCCESSED)

    def test_process__wait_confirmation__transaction_in_wrong_state(self):
        self.invoice.state = INVOICE_STATE.REJECTED
        self.invoice.save()

        self.task.state = BUY_PREMIUM_STATE.WAIT_TRANSACTION_CONFIRMATION

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state._is_ERROR_IN_CONFIRM_TRANSACTION)

    def test_process__wrong_state(self):
        self.task.state = BUY_PREMIUM_STATE.ERROR_IN_FREEZING_TRANSACTION

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state._is_WRONG_TASK_STATE)

        self.account.reload()
        self.assertTrue(self.account.premium_end_at < datetime.datetime.now())

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)
