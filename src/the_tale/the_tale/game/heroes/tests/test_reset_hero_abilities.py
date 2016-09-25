# coding: utf-8
import datetime

from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks.prototypes import POSTPONED_TASK_LOGIC_RESULT
from the_tale.common.postponed_tasks.tests.helpers import FakePostpondTaskPrototype

from the_tale.game.logic import create_test_map
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.heroes.habilities import battle as battle_abilities
from the_tale.game.heroes.postponed_tasks import ResetHeroAbilitiesTask

from .. import logic


class ResetHeroAbilitiesTest(TestCase):

    def setUp(self):
        super(ResetHeroAbilitiesTest, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.accounts_to_heroes[self.account.id]
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
