# coding: utf-8
import datetime

import mock

from django.db import IntegrityError

from dext.common.utils import s11n

from the_tale.common.utils import testcase
from the_tale.common.postponed_tasks import models as postponed_tasks_models
from the_tale.common.postponed_tasks import prototypes as postponed_prototypes

from the_tale.bank import prototypes as bank_prototypes
from the_tale.bank import models as bank_models
from the_tale.bank import transaction as bank_transaction

from the_tale.game.logic import create_test_map

from the_tale.market import conf
from the_tale.market import logic
from the_tale.market import models
from the_tale.market import relations
from the_tale.market import goods_types


class LogicTests(testcase.TransactionTestCase):

    def setUp(self):
        super(LogicTests, self).setUp()

        create_test_map()

        goods_types.autodiscover(if_empty=True)
        postponed_prototypes.autodiscover(if_empty=True)

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.goods_1 = logic.load_goods(self.account_1.id)

        self.good_1 = goods_types.test_hero_good.create_good('good-1')
        self.good_2 = goods_types.test_hero_good.create_good('good-2')
        self.good_3 = goods_types.test_hero_good.create_good('good-3')
        self.good_4 = goods_types.test_hero_good.create_good('good-4')

        self.goods_1.add_good(self.good_1)
        self.goods_1.add_good(self.good_2)
        self.goods_1.add_good(self.good_3)
        self.goods_1.add_good(self.good_4)
        logic.save_goods(self.goods_1)

        self.price = 666

        self.lot_1 = logic.reserve_lot(self.account_1.id, self.good_1, price=self.price)
        self.lot_1.state = relations.LOT_STATE.ACTIVE
        logic.save_lot(self.lot_1)

        goods_types.autodiscover(if_empty=True)


    def test_has_lot(self):
        self.assertTrue(logic.has_lot(account_id=self.account_1.id, good_uid=self.good_1.uid))
        self.assertFalse(logic.has_lot(account_id=666, good_uid=self.good_1.uid))
        self.assertFalse(logic.has_lot(account_id=self.account_1.id, good_uid='666'))
        self.assertFalse(logic.has_lot(account_id=666, good_uid='666'))

    def test_reserve_lot__unique_restrictions(self):
        with self.check_delta(models.Lot.objects.count, 0):
            self.assertRaises(IntegrityError,
                              logic.reserve_lot,
                              account_id=self.account_1.id,
                              good=self.good_1,
                              price=777)

    def test_reserve_lot(self):
        with self.check_delta(models.Lot.objects.count, 1):
            lot = logic.reserve_lot(account_id=self.account_1.id,
                                    good=self.good_2,
                                    price=777)

        lot_model = models.Lot.objects.latest()

        self.assertEqual(lot.id, lot_model.id)
        self.assertEqual(lot.type, lot_model.type)
        self.assertEqual(lot.seller_id, lot_model.seller_id)
        self.assertEqual(lot.buyer_id, lot_model.buyer_id)
        self.assertEqual(lot.name, lot_model.name)
        self.assertEqual(lot.state, lot_model.state)
        self.assertEqual(lot.price, lot_model.price)
        self.assertEqual(lot.good.serialize(), s11n.from_json(lot_model.data)['good'])

        self.assertEqual(lot.type, self.good_2.type)
        self.assertEqual(lot.seller_id, self.account_1.id)
        self.assertEqual(lot.buyer_id, None)
        self.assertEqual(lot.name, self.good_2.name)
        self.assertTrue(lot.state.is_RESERVED)
        self.assertEqual(lot.price, 777)
        self.assertEqual(lot.good.serialize(), self.good_2.serialize())


    def test_send_good_to_market(self):
        with mock.patch('the_tale.market.workers.market_manager.Worker.cmd_logic_task') as cmd_logic_task:
            with self.check_delta(postponed_tasks_models.PostponedTask.objects.count, 1):
                task = logic.send_good_to_market(seller_id=self.account_1.id, good=self.good_2, price=666)

        self.assertEqual(task.internal_logic.account_id, self.account_1.id)
        self.assertEqual(task.internal_logic.good_type, goods_types.test_hero_good.uid)
        self.assertEqual(task.internal_logic.good_uid, self.good_2.uid)
        self.assertEqual(task.internal_logic.price, 666)

        self.assertEqual(cmd_logic_task.call_args_list, [mock.call(self.account_1.id, task.id)])


    def test_purchase_lot(self):

        with mock.patch('the_tale.common.postponed_tasks.workers.refrigerator.Worker.cmd_wait_task') as cmd_wait_task:
            with self.check_delta(postponed_tasks_models.PostponedTask.objects.count, 1):
                with self.check_delta(bank_models.Invoice.objects.count, 1):
                    task = logic.purchase_lot(buyer_id=self.account_2.id, lot=self.lot_1)

        invoice = bank_prototypes.InvoicePrototype._db_latest()

        self.assertTrue(invoice.state.is_REQUESTED)
        self.assertTrue(invoice.recipient_type.is_GAME_ACCOUNT)
        self.assertTrue(invoice.sender_type.is_GAME_ACCOUNT)
        self.assertTrue(invoice.currency.is_PREMIUM)
        self.assertEqual(invoice.recipient_id, self.account_1.id)
        self.assertEqual(invoice.sender_id, self.account_2.id)
        self.assertEqual(invoice.amount, self.lot_1.price)

        self.assertEqual(task.internal_logic.seller_id, self.account_1.id)
        self.assertEqual(task.internal_logic.buyer_id, self.account_2.id)
        self.assertEqual(task.internal_logic.lot_id, self.lot_1.id)
        self.assertEqual(task.internal_logic.transaction.serialize(), bank_transaction.Transaction(invoice.id).serialize())

        self.assertEqual(cmd_wait_task.call_args_list, [mock.call(task.id)])


    def test_close_lots_by_timeout(self):
        lot_2 = logic.reserve_lot(self.account_1.id, self.good_2, price=2)
        lot_2.state = relations.LOT_STATE.ACTIVE
        logic.save_lot(lot_2)

        lot_3 = logic.reserve_lot(self.account_1.id, self.good_3, price=3)
        self.assertFalse(lot_3.state.is_ACTIVE)

        lot_4 = logic.reserve_lot(self.account_1.id, self.good_4, price=4)
        lot_4.state = relations.LOT_STATE.ACTIVE
        logic.save_lot(lot_4)

        models.Lot.objects.filter(id__in=[self.lot_1.id, lot_3.id, lot_4.id]).update(created_at=datetime.datetime.now()-datetime.timedelta(days=conf.settings.LOT_LIVE_TIME+1))

        with mock.patch('the_tale.market.workers.market_manager.Worker.cmd_logic_task') as cmd_logic_task:
            with self.check_delta(postponed_tasks_models.PostponedTask.objects.count, 2):
                tasks = logic.close_lots_by_timeout()

        self.assertEqual(cmd_logic_task.call_count, 2)

        self.assertEqual(tasks[0].internal_logic.lot_id, self.lot_1.id)
        self.assertEqual(tasks[1].internal_logic.lot_id, lot_4.id)
