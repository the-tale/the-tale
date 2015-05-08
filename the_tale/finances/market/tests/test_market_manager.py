# coding: utf-8

import mock

from the_tale.common.utils import testcase

from the_tale import amqp_environment

from the_tale.game.logic import create_test_map

from the_tale.finances.market import logic
from the_tale.finances.market import goods_types


class MarketManagerTests(testcase.TransactionTestCase):

    def setUp(self):
        super(MarketManagerTests, self).setUp()

        create_test_map()

        self.worker = amqp_environment.environment.workers.market_manager
        self.worker.initialize()

        self.account_1 = self.accounts_factory.create_account()

        self.goods_1 = logic.load_goods(self.account_1.id)

        self.good_1 = goods_types.test_hero_good.create_good('good-1')
        logic.save_goods(self.goods_1)

    def test_initialized(self):
        self.assertTrue(self.worker.initialized)


    def test_process_no_cmd(self):
        with mock.patch('the_tale.finances.market.logic.close_lots_by_timeout') as close_lots_by_timeout:
            self.worker.process_no_cmd()

        self.assertEqual(close_lots_by_timeout.call_count, 1)

    def test_process_logic_task(self):
        task = logic.send_good_to_market(seller_id=self.account_1.id, good=self.good_1, price=666)

        with mock.patch('the_tale.common.postponed_tasks.PostponedTaskPrototype.process') as process:
            with mock.patch('the_tale.common.postponed_tasks.PostponedTaskPrototype.do_postsave_actions') as do_postsave_actions:
                self.worker.process_logic_task(self.account_1.id, task.id)

        self.assertEqual(process.call_count, 1)
        self.assertEqual(do_postsave_actions.call_count, 1)

    def test_process_add_item(self):
        good_2 = goods_types.test_hero_good.create_good('good-2')

        self.assertFalse(self.goods_1.has_good(good_2.uid))

        self.worker.process_add_item(self.account_1.id, good_2.serialize())

        goods_1 = logic.load_goods(self.account_1.id)

        self.assertTrue(goods_1.has_good(good_2.uid))


    def process_remove_item(self):
        self.assertTrue(self.goods_1.has_good(self.good_1.uid))

        self.worker.process_remove_item(self.account_1.id, self.good_1.serialize())

        goods_1 = logic.load_goods(self.account_1.id)

        self.assertFalse(goods_1.has_good(self.good_1.uid))
