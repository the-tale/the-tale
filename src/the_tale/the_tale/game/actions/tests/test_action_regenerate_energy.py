
import time
from unittest import mock

from the_tale.common.utils import testcase

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map
from the_tale.game.actions.prototypes import ActionRegenerateEnergyPrototype

from the_tale.game import turn
from the_tale.game import tt_api_energy


class RegenerateEnergyActionTest(testcase.TestCase):

    def setUp(self):
        super(RegenerateEnergyActionTest, self).setUp()
        create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]
        self.action_idl = self.hero.actions.current_action

        self.action_regenerate = ActionRegenerateEnergyPrototype.create(hero=self.hero)

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_regenerate.leader, True)
        self.assertEqual(self.action_regenerate.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()

    def test_not_ready(self):
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_regenerate)
        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.can_regenerate_double_energy', False)
    def test_full(self):

        with self.check_delta(lambda: tt_api_energy.energy_balance(self.hero.account_id),
                              self.hero.preferences.energy_regeneration_type.amount):

            while len(self.hero.actions.actions_list) != 1:
                self.storage.process_turn(continue_steps_if_needed=False)
                turn.increment()

            time.sleep(0.1)

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.need_regenerate_energy, False)
        self.assertEqual(self.hero.last_energy_regeneration_at_turn, turn.number()-1)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.can_regenerate_double_energy', False)
    @mock.patch('the_tale.game.heroes.objects.Hero.can_regenerate_energy', False)
    def test_full__regeneration_restricted(self):

        with self.check_not_changed(lambda: tt_api_energy.energy_balance(self.hero.account_id)):

            while len(self.hero.actions.actions_list) != 1:
                self.storage.process_turn(continue_steps_if_needed=False)
                turn.increment()

            time.sleep(0.1)

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.need_regenerate_energy, False)
        self.assertEqual(self.hero.last_energy_regeneration_at_turn, turn.number()-1)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.can_regenerate_double_energy', True)
    def test_full__double_energy(self):
        with self.check_delta(lambda: tt_api_energy.energy_balance(self.hero.account_id),
                              self.hero.preferences.energy_regeneration_type.amount * 2):

            while len(self.hero.actions.actions_list) != 1:
                self.storage.process_turn(continue_steps_if_needed=False)
                turn.increment()

            time.sleep(0.1)

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.need_regenerate_energy, False)
        self.assertEqual(self.hero.last_energy_regeneration_at_turn, turn.number()-1)

        self.storage._test_save()
