# coding: utf-8
import random
import datetime

import mock

from the_tale.common.utils import testcase
from the_tale.common.postponed_tasks import POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts import logic as accounts_logic

from the_tale.accounts.personal_messages import prototypes as personal_messages_prototypes


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

        goods_types.test_hero_good._clear()

        self.good_1_uid = 'good-1'

        self.account_1 = self.accounts_factory.create_account()
        self.goods_1 = logic.load_goods(self.account_1.id)

        self.good_1 = goods_types.test_hero_good.create_good(self.good_1_uid)

        self.goods_1.add_good(self.good_1)
        logic.save_goods(self.goods_1)

        self.logic_storage = logic_storage.LogicStorage()
        self.hero_1 = self.logic_storage.load_account_data(self.account_1)

        self.price = 666

        self.lot_1 = logic.reserve_lot(self.account_1.id, self.good_1, price=self.price)
        self.lot_1.state = relations.LOT_STATE.ACTIVE
        logic.save_lot(self.lot_1)

        self.task = postponed_tasks.CloseLotByTimoutTask(lot_id=self.lot_1.id)

        self.main_task = mock.Mock(comment=None, id=777)


    def test_serialization(self):
        self.assertEqual(self.task.serialize(), postponed_tasks.CloseLotByTimoutTask.deserialize(self.task.serialize()).serialize())


    def test_initialization(self):
        self.assertTrue(self.task.state.is_UNPROCESSED)
        self.assertTrue(self.task.step.is_FREEZE_LOT)
        self.assertEqual(self.task.lot_id, self.lot_1.id)
        self.assertEqual(self.task.account_id, None)
        self.assertEqual(self.task.good_type, None)
        self.assertEqual(self.task.good, None)


    def test_freeze_lot__wrong_lot_state(self):
        self.lot_1.state = random.choice([state
                                          for state in relations.LOT_STATE.records
                                          if not state.is_ACTIVE])
        logic.save_lot(self.lot_1)

        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertTrue(self.task.state.is_WRONG_LOT_STATE)
        self.assertTrue(self.task.step.is_FREEZE_LOT)


    def test_freeze_lot__continue(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.assertTrue(self.task.state.is_UNPROCESSED)
        self.assertTrue(self.task.step.is_RETURN_GOOD)

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_logic_task') as cmd_logic_task:
            for call in self.main_task.extend_postsave_actions.call_args_list:
                for func in call[0][0]:
                    func()

        self.assertEqual(cmd_logic_task.call_count, 1)


    def test_return_good(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)
        self.assertEqual(self.task.process(self.main_task, storage=self.logic_storage), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        self.assertEqual(goods_types.test_hero_good.inserted_goods, [(self.hero_1.id, self.good_1.uid)])

        self.assertTrue(self.task.state.is_UNPROCESSED)
        self.assertTrue(self.task.step.is_CLOSE_LOT)

        with mock.patch('the_tale.market.workers.market_manager.Worker.cmd_logic_task') as cmd_logic_task:
            for call in self.main_task.extend_postsave_actions.call_args_list:
                for func in call[0][0]:
                    func()

        self.assertEqual(cmd_logic_task.call_count, 1)

    def test_close_lot(self):
        self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)
        self.assertEqual(self.task.process(self.main_task, storage=self.logic_storage), POSTPONED_TASK_LOGIC_RESULT.CONTINUE)

        with self.check_delta(personal_messages_prototypes.MessagePrototype._db_count, 1):
            self.assertEqual(self.task.process(self.main_task), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertTrue(self.task.state.is_PROCESSED)
        self.assertTrue(self.task.step.is_SUCCESS)

        lot = logic.load_lot(self.task.lot_id)
        self.assertTrue(lot.state.is_CLOSED_BY_TIMEOUT)
        self.assertTrue(lot.closed_at < datetime.datetime.now())
        self.assertEqual(lot.buyer_id, None)

        personal_message = personal_messages_prototypes.MessagePrototype._db_all().latest()

        self.assertEqual(personal_message.recipient_id, self.account_1.id)
        self.assertEqual(personal_message.sender_id, accounts_logic.get_system_user().id)
