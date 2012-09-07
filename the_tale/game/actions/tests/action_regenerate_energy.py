# coding: utf-8
from django.test import TestCase

from dext.settings import settings

from game.balance import formulas as f
from game.logic import create_test_bundle, create_test_map, test_bundle_save
from game.actions.prototypes import ActionRegenerateEnergyPrototype
from game.prototypes import TimePrototype


class RegenerateEnergyActionTest(TestCase):

    def setUp(self):
        settings.refresh()

        create_test_map()

        self.bundle = create_test_bundle('RegenerateActionTest')
        self.action_idl = self.bundle.tests_get_last_action()
        self.action_regenerate = ActionRegenerateEnergyPrototype.create(self.action_idl)
        self.hero = self.bundle.tests_get_hero()
        self.angel = self.bundle.tests_get_angel()

    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.hero.angel_id, self.angel.id)
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_regenerate.leader, True)
        test_bundle_save(self, self.bundle)

    def test_not_ready(self):
        self.bundle.process_turn()
        self.assertEqual(len(self.bundle.actions), 2)
        self.assertEqual(self.bundle.tests_get_last_action(), self.action_regenerate)
        test_bundle_save(self, self.bundle)

    def test_full(self):
        self.angel.change_energy(-self.angel.energy)

        current_time = TimePrototype.get_current_time()

        while len(self.bundle.actions) != 1:
            self.bundle.process_turn()
            current_time.increment_turn()

        self.assertTrue(self.action_idl.leader)
        self.assertEqual(self.angel.energy, f.angel_energy_regeneration_amount(self.hero.preferences.energy_regeneration_type))
        self.assertEqual(self.hero.need_regenerate_energy, False)
        self.assertEqual(self.hero.last_energy_regeneration_at_turn, TimePrototype.get_current_turn_number()-1)

        test_bundle_save(self, self.bundle)
