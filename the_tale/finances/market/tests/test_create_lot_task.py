# coding: utf-8
import mock

from the_tale.common.utils import testcase
from the_tale.common.postponed_tasks import POSTPONED_TASK_LOGIC_RESULT

from the_tale.game import logic_storage

from the_tale.finances.market import postponed_tasks
from the_tale.finances.market import logic
from the_tale.finances.market import models
from the_tale.finances.market import objects
from the_tale.finances.market import goods_types

from the_tale.game.logic import create_test_map


class TaskTests(testcase.TestCase):

    def setUp(self):
        super(TaskTests, self).setUp()

        create_test_map()

        self.good_1_uid = 'good-1'

        self.account_1 = self.accounts_factory.create_account()
        self.goods_1 = logic.load_goods(self.account_1.id)

        self.good_1 = goods_types.test_hero_good.create_good(self.good_1_uid)

        self.goods_1.add_good(self.good_1)
        logic.save_goods(self.goods_1)

        self.logic_storage = logic_storage.LogicStorage()
        self.logic_storage.load_account_data(self.account_1)

        self.price_1 = 666

        self.task = postponed_tasks.CreateLotTask(account_id=self.account_1.id,
                                                  good_type=goods_types.test_hero_good.uid,
                                                  good_uid=self.good_1_uid,
                                                  price=self.price_1)

        self.main_task = mock.Mock(comment=None, id=777)

    def test_serialization(self):
        self.assertEqual(self.task.serialize(), postponed_tasks.CreateLotTask.deserialize(self.task.serialize()).serialize())


    def test_initialization(self):
        self.assertTrue(self.task.state.is_UNPROCESSED)
        self.assertTrue(self.task.step.is_UNPROCESSED)
        self.assertEqual(self.task.account_id, self.account_1.id)
        self.assertEqual(self.task.good_type, goods_types.test_hero_good.uid)
        self.assertEqual(self.task.good_uid, self.good_1_uid)
        self.assertEqual(self.task.price, self.price_1)


    def test_banned(self):
        self.account_1.ban_game(1)
        self.account_1.save()

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state.is_BANNED)
        self.assertTrue(self.task.step.is_UNPROCESSED)


    def test_no_good(self):
        self.goods_1.remove_good(self.good_1_uid)
        logic.save_goods(self.goods_1)

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state.is_NO_GOOD)
        self.assertTrue(self.task.step.is_UNPROCESSED)

    def test_has_lot(self):
        logic.reserve_lot(self.account_1.id, self.goods_1.get_good(self.good_1_uid), price=777)

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.task.state.is_ALREADY_RESERVED)
        self.assertTrue(self.task.step.is_UNPROCESSED)

    def test_has_lot__other_good(self):
        good_2 = goods_types.test_hero_good.create_good('good-2')
        self.goods_1.add_good(good_2)
        logic.save_goods(self.goods_1)

        logic.reserve_lot(self.account_1.id, self.goods_1.get_good('good-2'), price=777)

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)
        self.assertTrue(self.task.state.is_UNPROCESSED)
        self.assertTrue(self.task.step.is_RESERVED)

    def test_has_lot__other_account(self):
        account_2 = self.accounts_factory.create_account()
        good_2 = goods_types.test_hero_good.create_good(self.good_1_uid)
        goods_2 = logic.load_goods(account_2.id)
        goods_2.add_good(good_2)
        logic.save_goods(goods_2)

        logic.reserve_lot(account_2.id, goods_2.get_good(self.good_1_uid), price=777)

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)
        self.assertTrue(self.task.state.is_UNPROCESSED)
        self.assertTrue(self.task.step.is_RESERVED)

    def test_reserved(self):
        with self.check_delta(models.Lot.objects.count, 1):
            self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.assertTrue(self.task.state.is_UNPROCESSED)
        self.assertTrue(self.task.step.is_RESERVED)

        lot = objects.Lot.from_model(models.Lot.objects.latest())

        self.assertEqual(lot.type, goods_types.test_hero_good.uid)
        self.assertEqual(lot.name, self.good_1.name)
        self.assertEqual(lot.seller_id, self.account_1.id)
        self.assertEqual(lot.buyer_id, None)
        self.assertTrue(lot.state.is_RESERVED)
        self.assertEqual(lot.good.uid, self.good_1_uid)
        self.assertEqual(lot.price, self.price_1)

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_logic_task') as cmd_logic_task:
            for call in self.main_task.extend_postsave_actions.call_args_list:
                for func in call[0][0]:
                    func()

        self.assertEqual(cmd_logic_task.call_count, 1)

    def test_hero_has_no_good(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        goods_types.test_hero_good.remove_good(self.good_1_uid)

        self.assertEqual(self.task.process(self.main_task, storage=self.logic_storage), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)
        self.assertTrue(self.task.state.is_NO_GOOD)
        self.assertTrue(self.task.step.is_ROLLBACK)

    def test_gotten(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.assertEqual(self.task.process(self.main_task, storage=self.logic_storage), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)
        self.assertTrue(self.task.state.is_UNPROCESSED)
        self.assertTrue(self.task.step.is_GOTTEN)

        with mock.patch('the_tale.finances.market.workers.market_manager.Worker.cmd_logic_task') as cmd_logic_task:
            for call in self.main_task.extend_postsave_actions.call_args_list:
                for func in call[0][0]:
                    func()

        self.assertEqual(cmd_logic_task.call_count, 1)


    def test_rollback(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        goods_types.test_hero_good.remove_good(self.good_1_uid)

        self.assertEqual(self.task.process(self.main_task, storage=self.logic_storage), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        with self.check_not_changed(models.Lot.objects.count):
            self.assertEqual(self.task.process(self.main_task, storage=self.logic_storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        lot = logic.load_lot(self.task.lot_id)
        self.assertTrue(lot.state.is_CLOSED_BY_ERROR)

        self.assertTrue(self.task.state.is_PROCESSED)
        self.assertTrue(self.task.step.is_ROLLBACKED)


    def test_activated(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)
        self.assertEqual(self.task.process(self.main_task, storage=self.logic_storage), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        with self.check_not_changed(models.Lot.objects.count):
            self.assertEqual(self.task.process(self.main_task, storage=self.logic_storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertTrue(self.task.state.is_PROCESSED)
        self.assertTrue(self.task.step.is_ACTIVATED)

        goods_1 = logic.load_goods(self.account_1.id)
        self.assertEqual(goods_1.goods_count(), 0)

        lot = objects.Lot.from_model(models.Lot.objects.latest())
        self.assertTrue(lot.state.is_ACTIVE)
