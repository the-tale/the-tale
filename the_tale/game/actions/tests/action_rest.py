# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map
from the_tale.game.actions.prototypes import ActionRestPrototype
from the_tale.game.abilities.deck.help import Help
from the_tale.game.abilities.relations import HELP_CHOICES
from the_tale.game.prototypes import TimePrototype

from the_tale.game.abilities.tests.helpers import UseAbilityTaskMixin

class RestActionTest(UseAbilityTaskMixin, testcase.TestCase):
    PROCESSOR = Help

    def setUp(self):
        super(RestActionTest, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]
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
        self.storage.process_turn(second_step_if_needed=False)
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

        self.hero.health = 1

        old_percents = self.action_rest.percents

        ability = self.PROCESSOR()

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: HELP_CHOICES.HEAL):
            self.assertTrue(ability.use(**self.use_attributes(hero=self.hero, storage=self.storage)))
            self.assertTrue(self.hero.health > 1)
            self.assertTrue(old_percents < self.action_rest.percents)
            self.assertEqual(self.hero.actions.current_action.percents, self.action_rest.percents)

    def test_full(self):
        self.hero.health = 1

        current_time = TimePrototype.get_current_time()

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(second_step_if_needed=False)
            current_time.increment_turn()

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.health, self.hero.max_health)

        self.storage._test_save()
