
from unittest import mock

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map
from the_tale.game.actions.prototypes import ActionRestPrototype
from the_tale.game.abilities.deck.help import Help
from the_tale.game.abilities.relations import HELP_CHOICES
from the_tale.game import turn

from the_tale.game.abilities.tests.helpers import UseAbilityTaskMixin


class RestActionTest(UseAbilityTaskMixin, testcase.TestCase):
    PROCESSOR = Help

    def setUp(self):
        super(RestActionTest, self).setUp()

        create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]
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
        self.storage.process_turn(continue_steps_if_needed=False)
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


    def test_ability_heal__healed(self):

        self.hero.health = self.hero.max_health - 1

        ability = self.PROCESSOR()

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: HELP_CHOICES.HEAL):
            self.assertTrue(ability.use(**self.use_attributes(hero=self.hero, storage=self.storage)))

        self.assertEqual(self.hero.health, self.hero.max_health)
        self.assertTrue(self.action_rest.percents, 1)
        self.assertEqual(self.action_rest.state, self.action_rest.STATE.PROCESSED)

    def test_full(self):
        self.hero.health = 1

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)
            turn.increment()

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.health, self.hero.max_health)

        self.storage._test_save()
