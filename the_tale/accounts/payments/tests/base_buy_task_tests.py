# coding: utf-8

import mock

from the_tale.common.utils import testcase

from the_tale.common.postponed_tasks import POSTPONED_TASK_LOGIC_RESULT

from the_tale.bank.transaction import Transaction
from the_tale.bank.prototypes import InvoicePrototype, AccountPrototype as BankAccountPrototype
from the_tale.bank.relations import ENTITY_TYPE, CURRENCY_TYPE, INVOICE_STATE

from the_tale.game.logic import create_test_map

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user


class BaseBuyPosponedTaskTests(testcase.TestCase):


    def setUp(self):
        super(BaseBuyPosponedTaskTests, self).setUp()

        create_test_map()

        self.initial_amount = 500
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

        self.transaction = Transaction(self.invoice.id)

        self.task = None
        self.storage = None
        self.cmd_update_with_account_data__call_count = 1
        self.accounts_manages_worker = True
        self.supervisor_worker = False

    def test_create(self):
        self.assertTrue(self.task.state._is_TRANSACTION_REQUESTED)
        self._test_create()

    def test_serialization(self):
        self.assertEqual(self.task.serialize(), self.task.__class__.deserialize(self.task.serialize()).serialize())

    def test_process__transaction_requested__invoice_unprocessed(self):
        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.WAIT)
        self.assertTrue(self.task.state._is_TRANSACTION_REQUESTED)

        self._test_process__transaction_requested__invoice_unprocessed()

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)

    def test_process__transaction_requested__invoice_rejected(self):
        self.invoice.state = INVOICE_STATE.REJECTED
        self.invoice.save()

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state._is_TRANSACTION_REJECTED)

        self._test_process__transaction_requested__invoice_rejected()

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)

    def test_process__transaction_requested__invoice_wrong_state(self):
        self.invoice.state = INVOICE_STATE.CONFIRMED
        self.invoice.save()

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state._is_ERROR_IN_FREEZING_TRANSACTION)

        self._test_process__transaction_requested__invoice_wrong_state()

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)

    def test_process__transaction_requested__invoice_frozen(self):
        self.invoice.state = INVOICE_STATE.FROZEN
        self.invoice.save()

        main_task = mock.Mock()

        self.assertEqual(self.task.process(main_task=main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)
        self.assertTrue(self.task.state._is_TRANSACTION_FROZEN)

        with mock.patch('the_tale.accounts.workers.accounts_manager.Worker.cmd_task') as cmd_task:
            with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_logic_task') as cmd_logic_task:
                postsave_actions = main_task.extend_postsave_actions.call_args[0][0]
                for action in postsave_actions:
                    action()

        if self.accounts_manages_worker:
            self.assertEqual(cmd_task.call_count, 1)

        if self.supervisor_worker:
            self.assertEqual(cmd_logic_task.call_count, 1)

        self._test_process__transaction_requested__invoice_frozen()

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)

    def test_process__transaction_frozen(self):
        self.invoice.state = INVOICE_STATE.FROZEN
        self.invoice.save()

        self.task.state = self.task.RELATION.TRANSACTION_FROZEN

        with mock.patch('the_tale.game.heroes.prototypes.HeroPrototype.cmd_update_with_account_data') as cmd_update_with_account_data:
            with mock.patch('the_tale.bank.transaction.Transaction.confirm') as transaction_confirm:
                self.assertEqual(self.task.process(main_task=mock.Mock(), storage=self.storage), POSTPONED_TASK_LOGIC_RESULT.WAIT)

        self.assertEqual(cmd_update_with_account_data.call_count, self.cmd_update_with_account_data__call_count)
        self.assertEqual(transaction_confirm.call_count, 1)

        self._test_process__transaction_frozen()

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount) # money will be withdrawed after transaction confirm processed

    def test_process__wait_confirmation__transaction_frozen(self):
        self.invoice.state = INVOICE_STATE.FROZEN
        self.invoice.save()

        self.task.state = self.task.RELATION.WAIT_TRANSACTION_CONFIRMATION

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.WAIT)
        self.assertTrue(self.task.state._is_WAIT_TRANSACTION_CONFIRMATION)

    def test_process__wait_confirmation__transaction_confirmed(self):
        self.invoice.state = INVOICE_STATE.CONFIRMED
        self.invoice.save()

        self.task.state = self.task.RELATION.WAIT_TRANSACTION_CONFIRMATION

        with mock.patch('the_tale.accounts.payments.postponed_tasks.BaseBuyTask.process_referrals') as process_referrals:
            self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(process_referrals.call_count, 1)

        self.assertTrue(self.task.state._is_SUCCESSED)

    def test_process__wait_confirmation__transaction_confirmed__with_referal(self):
        self.invoice.state = INVOICE_STATE.CONFIRMED
        self.invoice.save()

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account._model.referral_of_id = account_id
        self.account.save()

        self.task.state = self.task.RELATION.WAIT_TRANSACTION_CONFIRMATION

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(InvoicePrototype._db_count(), 2)

        referral_invoice = InvoicePrototype._db_get_object(1)

        self.assertTrue(referral_invoice.amount > 0)
        self.assertTrue(referral_invoice.amount < self.amount)
        self.assertEqual(referral_invoice.recipient_id, account_id)
        self.assertTrue(referral_invoice.state._is_FORCED)

        self.assertTrue(self.task.state._is_SUCCESSED)

    def test_process__wait_confirmation__transaction_in_wrong_state(self):
        self.invoice.state = INVOICE_STATE.REJECTED
        self.invoice.save()

        self.task.state = self.task.RELATION.WAIT_TRANSACTION_CONFIRMATION

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state._is_ERROR_IN_CONFIRM_TRANSACTION)

    def test_process__wrong_state(self):
        self.task.state = self.task.RELATION.ERROR_IN_FREEZING_TRANSACTION

        self.assertEqual(self.task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state._is_WRONG_TASK_STATE)

        self._test_process__wrong_state()

        self.bank_account.reload()
        self.assertEqual(self.bank_account.amount, self.initial_amount)
