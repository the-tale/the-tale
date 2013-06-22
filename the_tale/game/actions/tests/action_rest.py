# coding: utf-8
import mock

from common.utils import testcase

from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype
from game.logic_storage import LogicStorage


from game.balance import constants as c
from game.logic import create_test_map
from game.actions.prototypes import ActionRestPrototype
from game.abilities.deck.help import Help
from game.prototypes import TimePrototype

class RestActionTest(testcase.TestCase):

    def setUp(self):
        super(RestActionTest, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.hero.actions.current_action

        self.action_rest = ActionRestPrototype.create(hero=self.hero)

    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_rest.leader, True)
        self.assertEqual(self.action_rest.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()

    def test_processed(self):
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.storage._test_save()

    def test_not_ready(self):
        self.hero.health = 1
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_rest)
        self.assertTrue(self.hero.health > 1)
        self.storage._test_save()

    def test_ability_heal(self):

        ability = Help()

        self.hero.health = 1

        old_percents = self.action_rest.percents

        with mock.patch('game.actions.prototypes.ActionBase.get_help_choice', lambda x: c.HELP_CHOICES.HEAL):
            self.assertTrue(ability.use(storage=self.storage, data={'hero_id': self.hero.id}, step=None, main_task_id=0, pvp_balancer=None))
            self.assertTrue(self.hero.health > 1)
            self.assertTrue(old_percents < self.action_rest.percents)
            self.assertEqual(self.hero.actions.current_action.percents, self.action_rest.percents)

    def test_full(self):
        self.hero.health = 1

        current_time = TimePrototype.get_current_time()

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.health, self.hero.max_health)

        self.storage._test_save()
