# coding: utf-8
import mock
from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.balance import formulas as f
from the_tale.game.logic import create_test_map
from the_tale.game.actions.prototypes import ActionRegenerateEnergyPrototype
from the_tale.game.prototypes import TimePrototype


class RegenerateEnergyActionTest(testcase.TestCase):

    def setUp(self):
        super(RegenerateEnergyActionTest, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]
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
        self.hero.change_energy(-self.hero.energy)

        current_time = TimePrototype.get_current_time()

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)
            current_time.increment_turn()

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.energy, self.hero.preferences.energy_regeneration_type.amount)
        self.assertEqual(self.hero.need_regenerate_energy, False)
        self.assertEqual(self.hero.last_energy_regeneration_at_turn, TimePrototype.get_current_turn_number()-1)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.can_regenerate_double_energy', True)
    def test_full__double_energy(self):
        self.hero.change_energy(-self.hero.energy)

        current_time = TimePrototype.get_current_time()

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)
            current_time.increment_turn()

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.energy, self.hero.preferences.energy_regeneration_type.amount * 2)
        self.assertEqual(self.hero.need_regenerate_energy, False)
        self.assertEqual(self.hero.last_energy_regeneration_at_turn, TimePrototype.get_current_turn_number()-1)

        self.storage._test_save()
