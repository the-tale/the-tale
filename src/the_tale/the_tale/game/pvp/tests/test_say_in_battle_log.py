# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.common.postponed_tasks.prototypes import POSTPONED_TASK_LOGIC_RESULT
from the_tale.common.postponed_tasks.tests.helpers import FakePostpondTaskPrototype

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.pvp.prototypes import Battle1x1Prototype
from the_tale.game.pvp.postponed_tasks import SayInBattleLogTask, SAY_IN_HERO_LOG_TASK_STATE

class SayInBattleLogTests(testcase.TestCase):

    def setUp(self):
        super(SayInBattleLogTests, self).setUp()

        self.p1, self.p2, self.p3 = create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        self.battle = Battle1x1Prototype.create(self.account_1)
        self.battle.set_enemy(self.account_2)
        self.battle.save()

        self.task = SayInBattleLogTask(battle_id=self.battle.id, text='some pvp message')

    def test_create(self):
        self.assertEqual(self.task.state, SAY_IN_HERO_LOG_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.task.battle_id, self.battle.id)

    def test_serialize(self):
        self.assertEqual(self.task.serialize(), SayInBattleLogTask.deserialize(self.task.serialize()).serialize())

    def test_process_account_hero_not_found(self):
        self.storage.release_account_data(self.account_1.id)
        self.task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(self.task.state, SAY_IN_HERO_LOG_TASK_STATE.ACCOUNT_HERO_NOT_FOUND)

    def test_process_battle_not_found(self):
        self.storage.release_account_data(self.account_1.id)
        self.battle.remove()
        self.task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(self.task.state, SAY_IN_HERO_LOG_TASK_STATE.BATTLE_NOT_FOUND)

    def test_process_success(self):
        self.assertFalse(self.hero_1.journal.messages)
        self.assertFalse(self.hero_2.journal.messages)

        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, SAY_IN_HERO_LOG_TASK_STATE.PROCESSED)

        self.assertTrue(self.hero_1.journal.messages)
        self.assertTrue(self.hero_2.journal.messages)


    def test_process_success_without_second_hero(self):
        self.assertFalse(self.hero_1.journal.messages)
        self.assertFalse(self.hero_2.journal.messages)

        self.storage.release_account_data(self.account_2.id)
        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(self.task.state, SAY_IN_HERO_LOG_TASK_STATE.PROCESSED)

        self.assertTrue(self.hero_1.journal.messages)
        self.assertFalse(self.hero_2.journal.messages)
