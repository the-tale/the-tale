# coding: utf-8
import mock

from the_tale.common.utils import testcase
from the_tale.common.postponed_tasks import POSTPONED_TASK_LOGIC_RESULT

from the_tale.finances.bank import transaction as bank_transaction
from the_tale.finances.bank import prototypes as bank_prototypes
from the_tale.finances.bank import relations as bank_relations

from the_tale.game.logic import create_test_map

from the_tale.accounts.personal_messages import prototypes as personal_messages_prototypes

from the_tale.accounts import postponed_tasks
from the_tale.accounts import logic



class TransferMoneyTaskTests(testcase.TestCase):

    def setUp(self):
        super(TransferMoneyTaskTests, self).setUp()
        create_test_map()

        self.sender = self.accounts_factory.create_account()
        self.recipient = self.accounts_factory.create_account()

        self.task = postponed_tasks.TransferMoneyTask(sender_id=self.sender.id,
                                                      recipient_id=self.recipient.id,
                                                      amount=666,
                                                      commission=13,
                                                      comment=u'some comment string')

        self.main_task = mock.Mock(id=777)

    def test_initialization(self):
        self.assertTrue(self.task.state.is_UNPROCESSED)
        self.assertTrue(self.task.step.is_INITIALIZE)
        self.assertEqual(self.task.sender_id, self.sender.id)
        self.assertEqual(self.task.recipient_id, self.recipient.id)
        self.assertEqual(self.task.transfer_transaction, None)
        self.assertEqual(self.task.commission_transaction, None)
        self.assertEqual(self.task.comment, u'some comment string')
        self.assertEqual(self.task.amount, 666)
        self.assertEqual(self.task.commission, 13)

    def test_serialization(self):
        self.assertEqual(self.task.serialize(), postponed_tasks.TransferMoneyTask.deserialize(self.task.serialize()).serialize())

    def test_serialization__with_transactions(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)
        self.assertEqual(self.task.serialize(), postponed_tasks.TransferMoneyTask.deserialize(self.task.serialize()).serialize())

    def test_initialize__sender_is_fast(self):
        self.sender.is_fast = True
        self.sender.save()
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.step.is_ERROR)
        self.assertTrue(self.task.state.is_SENDER_IS_FAST)

    def test_initialize__sender_is_banned(self):
        self.sender.ban_game(1)
        self.sender.save()
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.step.is_ERROR)
        self.assertTrue(self.task.state.is_SENDER_BANNED)

    def test_initialize__recipient_is_fast(self):
        self.recipient.is_fast = True
        self.recipient.save()
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.step.is_ERROR)
        self.assertTrue(self.task.state.is_RECIPIENT_IS_FAST)

    def test_initialize__recipient_is_banned(self):
        self.recipient.ban_game(1)
        self.recipient.save()
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.step.is_ERROR)
        self.assertTrue(self.task.state.is_RECIPIENT_BANNED)

    def test_initialize__sucessed(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        transfer_invoice = self.task.transfer_transaction.get_invoice()

        self.assertTrue(transfer_invoice.recipient_type.is_GAME_ACCOUNT)
        self.assertEqual(transfer_invoice.recipient_id, self.recipient.id)
        self.assertTrue(transfer_invoice.sender_type.is_GAME_ACCOUNT)
        self.assertEqual(transfer_invoice.sender_id, self.sender.id)
        self.assertTrue(transfer_invoice.currency.is_PREMIUM)
        self.assertTrue(transfer_invoice.amount, 666)
        self.assertTrue(transfer_invoice.operation_uid, u'transfer-money-between-accounts-transfer')

        commission_invoice = self.task.commission_transaction.get_invoice()

        self.assertTrue(commission_invoice.recipient_type.is_GAME_ACCOUNT)
        self.assertEqual(commission_invoice.recipient_id, self.sender.id)
        self.assertTrue(commission_invoice.sender_type.is_GAME_LOGIC)
        self.assertEqual(commission_invoice.sender_id, 0)
        self.assertTrue(commission_invoice.currency.is_PREMIUM)
        self.assertTrue(commission_invoice.amount, 666)
        self.assertTrue(commission_invoice.operation_uid, u'transfer-money-between-accounts-commission')

        self.assertTrue(self.task.step.is_WAIT)
        self.assertTrue(self.task.state.is_UNPROCESSED)

        with mock.patch('the_tale.common.postponed_tasks.workers.refrigerator.Worker.cmd_wait_task') as cmd_wait_task:
            for call in self.main_task.extend_postsave_actions.call_args_list:
                for func in call[0][0]:
                    func()

        self.assertEqual(cmd_wait_task.call_count, 1)


    def test_wait__transfer_not_frozen_yet(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        commission_invoice = self.task.commission_transaction.get_invoice()
        commission_invoice.state = bank_relations.INVOICE_STATE.FROZEN
        commission_invoice.save()

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.WAIT)

        self.assertTrue(self.task.step.is_WAIT)
        self.assertTrue(self.task.state.is_UNPROCESSED)

    def test_wait__transfer_rejected(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        transfer_invoice = self.task.transfer_transaction.get_invoice()
        transfer_invoice.state = bank_relations.INVOICE_STATE.REJECTED
        transfer_invoice.save()

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertTrue(self.task.step.is_ERROR)
        self.assertTrue(self.task.state.is_TRANSFER_TRANSACTION_REJECTED)

    def test_wait__transfer_in_wrong_state(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        transfer_invoice = self.task.transfer_transaction.get_invoice()
        transfer_invoice.state = bank_relations.INVOICE_STATE.random(exclude=(bank_relations.INVOICE_STATE.REQUESTED,
                                                                              bank_relations.INVOICE_STATE.REJECTED,
                                                                              bank_relations.INVOICE_STATE.FROZEN))
        transfer_invoice.save()

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertTrue(self.task.step.is_ERROR)
        self.assertTrue(self.task.state.is_TRANSFER_TRANSACTION_WRONG_STATE)

    def test_wait__commission_not_frozen_yet(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        transfer_invoice = self.task.transfer_transaction.get_invoice()
        transfer_invoice.state = bank_relations.INVOICE_STATE.FROZEN
        transfer_invoice.save()

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.WAIT)

        self.assertTrue(self.task.step.is_WAIT)
        self.assertTrue(self.task.state.is_UNPROCESSED)

    def test_wait__commission_rejected(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        commission_invoice = self.task.commission_transaction.get_invoice()
        commission_invoice.state = bank_relations.INVOICE_STATE.FROZEN
        commission_invoice.save()

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.WAIT)

        self.assertTrue(self.task.step.is_WAIT)
        self.assertTrue(self.task.state.is_UNPROCESSED)

    def test_wait__commission_in_wrong_state(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        transfer_invoice = self.task.transfer_transaction.get_invoice()
        transfer_invoice.state = bank_relations.INVOICE_STATE.FROZEN
        transfer_invoice.save()

        commission_invoice = self.task.commission_transaction.get_invoice()
        commission_invoice.state = bank_relations.INVOICE_STATE.random(exclude=(bank_relations.INVOICE_STATE.REQUESTED,
                                                                                bank_relations.INVOICE_STATE.REJECTED,
                                                                                bank_relations.INVOICE_STATE.FROZEN))
        commission_invoice.save()

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertTrue(self.task.step.is_ERROR)
        self.assertTrue(self.task.state.is_COMMISSION_TRANSACTION_WRONG_STATE)

    def test_wait__successed(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        transfer_invoice = self.task.transfer_transaction.get_invoice()
        transfer_invoice.state = bank_relations.INVOICE_STATE.FROZEN
        transfer_invoice.save()

        commission_invoice = self.task.commission_transaction.get_invoice()
        commission_invoice.state = bank_relations.INVOICE_STATE.FROZEN
        commission_invoice.save()

        with self.check_delta(personal_messages_prototypes.MessagePrototype._db_count, 1):
            self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertTrue(self.task.step.is_SUCCESS)
        self.assertTrue(self.task.state.is_PROCESSED)

        message = personal_messages_prototypes.MessagePrototype._db_latest()

        self.assertEqual(message.sender_id, logic.get_system_user().id)
        self.assertEqual(message.recipient_id, self.recipient.id)
        self.assertIn(u'some comment string', message.text)
