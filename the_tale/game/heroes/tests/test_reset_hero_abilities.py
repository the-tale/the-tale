# coding: utf-8
import datetime

from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.heroes.habilities import battle as battle_abilities
from the_tale.game.heroes.postponed_tasks import ResetHeroAbilitiesTask

from .. import logic


class ResetHeroAbilitiesTest(TestCase):

    def setUp(self):
        super(ResetHeroAbilitiesTest, self).setUp()
        place_1, place_2, place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.accounts_to_heroes[account_id]
        self.hero.abilities.add(battle_abilities.STRONG_HIT.get_id())
        self.hero.abilities.set_reseted_at(datetime.datetime.fromtimestamp(0))
        logic.save_hero(self.hero)

    def test_create(self):
        task = ResetHeroAbilitiesTask(self.hero.id)
        self.assertTrue(task.state.is_UNPROCESSED)

    def test_serialization(self):
        task = ResetHeroAbilitiesTask(self.hero.id)
        self.assertEqual(task.serialize(), ResetHeroAbilitiesTask.deserialize(task.serialize()).serialize())

    def test_reset__timeout(self):
        task = ResetHeroAbilitiesTask(self.hero.id)

        self.hero.abilities.set_reseted_at(datetime.datetime.now())

        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertTrue(len(self.hero.abilities.all) > 1)
        self.assertTrue(task.state.is_RESET_TIMEOUT)

    def test_reset(self):
        task = ResetHeroAbilitiesTask(self.hero.id)

        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)

        self.assertEqual(len(self.hero.abilities.all), 2)
        self.assertTrue(task.state.is_PROCESSED)
