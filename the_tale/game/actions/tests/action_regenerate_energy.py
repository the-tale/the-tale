# coding: utf-8
from django.test import TestCase

from dext.settings import settings

from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype
from game.logic_storage import LogicStorage

from game.balance import formulas as f
from game.logic import create_test_map
from game.actions.prototypes import ActionRegenerateEnergyPrototype
from game.prototypes import TimePrototype


class RegenerateEnergyActionTest(TestCase):

    def setUp(self):
        settings.refresh()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.storage.heroes_to_actions[self.hero.id][-1]

        self.action_regenerate = ActionRegenerateEnergyPrototype.create(self.action_idl)

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_regenerate.leader, True)
        self.assertEqual(self.action_regenerate.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()

    def test_not_ready(self):
        self.storage.process_turn()
        self.assertEqual(len(self.storage.actions), 2)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1], self.action_regenerate)
        self.storage._test_save()

    def test_full(self):
        self.hero.change_energy(-self.hero.energy)

        current_time = TimePrototype.get_current_time()

        while len(self.storage.actions) != 1:
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.hero.energy, f.angel_energy_regeneration_amount(self.hero.preferences.energy_regeneration_type))
        self.assertEqual(self.hero.need_regenerate_energy, False)
        self.assertEqual(self.hero.last_energy_regeneration_at_turn, TimePrototype.get_current_turn_number()-1)

        self.storage._test_save()
