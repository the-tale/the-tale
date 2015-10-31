# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.pvp.prototypes import Battle1x1Prototype
from the_tale.game.pvp.postponed_tasks import SayInBattleLogTask, SAY_IN_HERO_LOG_TASK_STATE

class SayInBattleLogTests(testcase.TestCase):

    def setUp(self):
        super(SayInBattleLogTests, self).setUp()

        self.p1, self.p2, self.p3 = create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        result, account_2_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        self.battle = Battle1x1Prototype.create(self.account_1)
        self.battle.set_enemy(self.account_2)
        self.battle.save()

        self.task = SayInBattleLogTask(battle_id=self.battle.id, text=u'some pvp message')

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
        old_hero_1_last_message = self.hero_1.journal.messages[-1]
        old_hero_2_last_message = self.hero_2.journal.messages[-1]

        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, SAY_IN_HERO_LOG_TASK_STATE.PROCESSED)

        self.assertNotEqual(old_hero_1_last_message, self.hero_1.journal.messages[-1])
        self.assertNotEqual(old_hero_2_last_message, self.hero_2.journal.messages[-1])

    def test_process_success_without_second_hero(self):
        old_hero_1_last_message = self.hero_1.journal.messages[-1]
        old_hero_2_last_message = self.hero_2.journal.messages[-1]

        self.storage.release_account_data(self.account_2.id)
        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(self.task.state, SAY_IN_HERO_LOG_TASK_STATE.PROCESSED)
        self.assertNotEqual(old_hero_1_last_message, self.hero_1.journal.messages[-1])
        self.assertEqual(old_hero_2_last_message, self.hero_2.journal.messages[-1])
