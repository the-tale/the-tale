# coding: utf-8
import random
import datetime

import mock

from the_tale.common.utils import testcase
from the_tale.common.postponed_tasks import POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts import logic as accounts_logic

from the_tale.accounts.personal_messages import prototypes as personal_messages_prototypes

from the_tale.bank import transaction as bank_transaction
from the_tale.bank import prototypes as bank_prototypes
from the_tale.bank import relations as bank_relations

from the_tale.game import logic_storage

from the_tale.market import postponed_tasks
from the_tale.market import logic
from the_tale.market import relations
from the_tale.market import goods_types

from the_tale.game.logic import create_test_map


class TaskTests(testcase.TestCase):

    def setUp(self):
        super(TaskTests, self).setUp()

        create_test_map()

        goods_types.autodiscover()

        self.good_1_uid = 'good-1'

        self.account_1 = self.accounts_factory.create_account()
        self.goods_1 = logic.load_goods(self.account_1.id)

        self.account_2 = self.accounts_factory.create_account()
        self.goods_2 = logic.load_goods(self.account_2.id)

        self.good_1 = goods_types.test_hero_good.create_good(self.good_1_uid)

        self.goods_1.add_good(self.good_1)
        logic.save_goods(self.goods_1)

        self.logic_storage = logic_storage.LogicStorage()
        self.hero_1 = self.logic_storage.load_account_data(self.account_1)
        self.hero_2 = self.logic_storage.load_account_data(self.account_2)

        self.price = 666

        self.lot_1 = logic.reserve_lot(self.account_1.id, self.good_1, price=self.price)
        self.lot_1.state = relations.LOT_STATE.ACTIVE
        logic.save_lot(self.lot_1)

        self.invoice = bank_prototypes.InvoicePrototype.create(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                               recipient_id=self.account_1.id,
                                                               sender_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                               sender_id=self.account_2.id,
                                                               currency=bank_relations.CURRENCY_TYPE.PREMIUM,
                                                               amount=self.price,
                                                               description_for_sender='transaction-description-for_sender',
                                                               description_for_recipient='transaction-description-for-recipient',
                                                               operation_uid='transaction-operation-ui')


        self.transaction = bank_transaction.Transaction(self.invoice.id)

        self.task = postponed_tasks.BuyLotTask(seller_id=self.account_1.id,
                                               buyer_id=self.account_2.id,
                                               lot_id=self.lot_1.id,
                                               transaction=self.transaction)

        self.main_task = mock.Mock(comment=None, id=777)


    def test_serialization(self):
        self.assertEqual(self.task.serialize(), postponed_tasks.BuyLotTask.deserialize(self.task.serialize()).serialize())


    def test_initialization(self):
        self.assertTrue(self.task.state.is_UNPROCESSED)
        self.assertTrue(self.task.step.is_FREEZE_MONEY)
        self.assertEqual(self.task.lot_id, self.lot_1.id)
        self.assertEqual(self.task.seller_id, self.account_1.id)
        self.assertEqual(self.task.buyer_id, self.account_2.id)
        self.assertEqual(self.task.transaction, self.transaction)
        self.assertEqual(self.task.good_type, None)
        self.assertEqual(self.task.good, None)


    def test_freeze_money__transaction_requested(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.WAIT)
        self.assertTrue(self.task.state.is_UNPROCESSED)
        self.assertTrue(self.task.step.is_FREEZE_MONEY)


    def test_freeze_money__transaction_rejected(self):
        self.invoice.state = bank_relations.INVOICE_STATE.REJECTED
        self.invoice.save()

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state.is_TRANSACTION_REJECTED)
        self.assertTrue(self.task.step.is_FREEZE_MONEY)


    def test_freeze_money__transaction_not_frozen(self):
        self.invoice.state = random.choice([state
                                            for state in bank_relations.INVOICE_STATE.records
                                            if state not in (bank_relations.INVOICE_STATE.REJECTED,
                                                             bank_relations.INVOICE_STATE.REQUESTED,
                                                             bank_relations.INVOICE_STATE.FROZEN)])
        self.invoice.save()

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state.is_WRONG_TRANSACTION_STATE)
        self.assertTrue(self.task.step.is_FREEZE_MONEY)


    def test_freeze_money__transaction_frozen(self):
        self.invoice.state = bank_relations.INVOICE_STATE.FROZEN
        self.invoice.save()

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)
        self.assertTrue(self.task.state.is_UNPROCESSED)
        self.assertTrue(self.task.step.is_FREEZE_LOT)

        with mock.patch('the_tale.market.workers.market_manager.Worker.cmd_logic_task') as cmd_logic_task:
            for call in self.main_task.extend_postsave_actions.call_args_list:
                for func in call[0][0]:
                    func()

        self.assertEqual(cmd_logic_task.call_count, 1)


    def test_freeze_lot__seller_banned(self):
        self.invoice.state = bank_relations.INVOICE_STATE.FROZEN
        self.invoice.save()

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.account_1.ban_game(1)
        self.account_1.save()

        with mock.patch('the_tale.bank.transaction.Transaction.cancel') as cancel:
            self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.assertTrue(self.task.state.is_UNPROCESSED)
        self.assertTrue(self.task.step.is_RECEIVE_GOOD)

        self.assertEqual(cancel.call_count, 0)


    def test_freeze_lot__buyer_banned(self):
        self.invoice.state = bank_relations.INVOICE_STATE.FROZEN
        self.invoice.save()

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.account_2.ban_game(1)
        self.account_2.save()

        with mock.patch('the_tale.bank.transaction.Transaction.cancel') as cancel:
            self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertTrue(self.task.state.is_BUYER_BANNED)
        self.assertTrue(self.task.step.is_FREEZE_LOT)

        self.assertEqual(cancel.call_count, 1)


    def test_freeze_lot__lot_not_active(self):
        self.invoice.state = bank_relations.INVOICE_STATE.FROZEN
        self.invoice.save()

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.lot_1.state = random.choice([state
                                          for state in relations.LOT_STATE.records
                                          if not state.is_ACTIVE])
        logic.save_lot(self.lot_1)

        with mock.patch('the_tale.bank.transaction.Transaction.cancel') as cancel:
            self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertTrue(self.task.state.is_WRONG_LOT_STATE)
        self.assertTrue(self.task.step.is_FREEZE_LOT)

        self.assertEqual(cancel.call_count, 1)


    def test_freeze_lot__success(self):
        self.invoice.state = bank_relations.INVOICE_STATE.FROZEN
        self.invoice.save()

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.assertTrue(self.task.state.is_UNPROCESSED)
        self.assertTrue(self.task.step.is_RECEIVE_GOOD)

        lot = logic.load_lot(self.task.lot_id)

        self.assertTrue(lot.state.is_FROZEN)

        with mock.patch('the_tale.game.workers.logic.Worker.cmd_logic_task') as cmd_logic_task:
            for call in self.main_task.extend_postsave_actions.call_args_list:
                for func in call[0][0]:
                    func()

        self.assertEqual(cmd_logic_task.call_count, 1)


    def test_receive_good(self):
        self.invoice.state = bank_relations.INVOICE_STATE.FROZEN
        self.invoice.save()

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)
        self.assertEqual(self.task.process(self.main_task, storage=self.logic_storage), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.assertTrue(self.task.state.is_UNPROCESSED)
        self.assertTrue(self.task.step.is_REMOVE_LOT)

        with mock.patch('the_tale.market.workers.market_manager.Worker.cmd_logic_task') as cmd_logic_task:
            for call in self.main_task.extend_postsave_actions.call_args_list:
                for func in call[0][0]:
                    func()

        self.assertEqual(cmd_logic_task.call_count, 2)

        self.assertEqual(goods_types.test_hero_good.inserted_goods, [(self.hero_2.id, self.good_1.uid)])


    def test_remove_lot(self):
        self.invoice.state = bank_relations.INVOICE_STATE.FROZEN
        self.invoice.save()

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)
        self.assertEqual(self.task.process(self.main_task, storage=self.logic_storage), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        with mock.patch('the_tale.bank.transaction.Transaction.confirm') as confirm:
            with self.check_delta(bank_prototypes.InvoicePrototype._model_class.objects.count, 1):
                with self.check_delta(personal_messages_prototypes.MessagePrototype._db_count, 1):
                    self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(confirm.call_count, 1)

        self.assertTrue(self.task.state.is_PROCESSED)
        self.assertTrue(self.task.step.is_SUCCESS)

        lot = logic.load_lot(self.task.lot_id)
        self.assertTrue(lot.state.is_CLOSED_BY_BUYER)
        self.assertTrue(lot.closed_at < datetime.datetime.now())
        self.assertEqual(lot.buyer_id, self.account_2.id)

        personal_message = personal_messages_prototypes.MessagePrototype._db_all().latest()

        self.assertEqual(personal_message.recipient_id, self.account_1.id)
        self.assertEqual(personal_message.sender_id, accounts_logic.get_system_user().id)

        commission_ivoice = bank_prototypes.InvoicePrototype._db_latest()

        self.assertTrue(commission_ivoice.recipient_type.is_GAME_ACCOUNT)
        self.assertEqual(commission_ivoice.recipient_id, lot.seller_id)
        self.assertTrue(commission_ivoice.sender_type.is_GAME_LOGIC)
        self.assertEqual(commission_ivoice.sender_id, 0)
        self.assertTrue(commission_ivoice.currency.is_PREMIUM)
        self.assertEqual(commission_ivoice.amount, -lot.commission)
        self.assertEqual(commission_ivoice.operation_uid, u'market-buy-commission-%s' % lot.type)
        self.assertTrue(commission_ivoice.state.is_FORCED)
