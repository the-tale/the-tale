# coding: utf-8

from django.test import TestCase

from dext.settings import settings

from accounts.logic import register_user
from game.heroes.prototypes import HeroPrototype
from game.logic_storage import LogicStorage

from game.logic import create_test_map
from game.actions.prototypes import ActionIdlenessPrototype, ActionQuestPrototype, ActionInPlacePrototype, ActionRegenerateEnergyPrototype
from game.balance import constants as c, formulas as f
from game.prototypes import TimePrototype

class IdlenessActionTest(TestCase):

    def setUp(self):
        settings.refresh()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.storage.heroes_to_actions[self.hero.id][-1]

    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, True)
        self.storage._test_save()


    def test_first_quest(self):
        self.storage.process_turn()
        self.assertEqual(len(self.storage.actions), 2)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.QUEST)
        self.assertTrue(self.action_idl.updated)
        self.assertTrue(self.action_idl.bundle_id is not None)
        self.storage._test_save()


    def test_inplace(self):
        self.action_idl.state = ActionIdlenessPrototype.STATE.QUEST
        self.storage.process_turn()
        self.assertEqual(len(self.storage.actions), 2)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionInPlacePrototype.TYPE)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.IN_PLACE)
        self.storage._test_save()

    def test_waiting(self):
        self.action_idl.state = ActionIdlenessPrototype.STATE.IN_PLACE
        self.storage.process_turn()
        self.assertEqual(len(self.storage.actions), 1)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1], self.action_idl)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.WAITING)
        self.storage._test_save()

    def test_regenerate_energy_action_create(self):
        self.hero.preferences.energy_regeneration_type = c.ANGEL_ENERGY_REGENERATION_TYPES.PRAY
        self.hero.last_energy_regeneration_at_turn -= max([f.angel_energy_regeneration_delay(energy_regeneration_type)
                                                           for energy_regeneration_type in c.ANGEL_ENERGY_REGENERATION_STEPS.keys()])
        self.action_idl.percents = 0.0
        self.storage.process_turn()
        self.assertEqual(len(self.storage.actions), 2)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionRegenerateEnergyPrototype.TYPE)
        self.storage._test_save()

    def test_regenerate_energy_action_not_create_for_sacrifice(self):
        self.action_idl.percents = 0
        self.hero.preferences.energy_regeneration_type = c.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE
        self.hero.last_energy_regeneration_at_turn -= max([f.angel_energy_regeneration_delay(energy_regeneration_type)
                                                           for energy_regeneration_type in c.ANGEL_ENERGY_REGENERATION_STEPS.keys()])
        self.storage.process_turn()
        self.assertEqual(len(self.storage.actions), 1)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1], self.action_idl)
        self.storage._test_save()


    def test_full_waiting(self):
        self.action_idl.state = ActionIdlenessPrototype.STATE.WAITING
        self.action_idl.percents = 0

        current_time = TimePrototype.get_current_time()

        for i in xrange(c.TURNS_TO_IDLE-1):
            self.storage.process_turn()
            current_time.increment_turn()
            self.assertEqual(len(self.storage.actions), 1)
            self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1], self.action_idl)

        self.storage.process_turn()

        self.assertEqual(len(self.storage.actions), 2)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.QUEST)

        self.storage._test_save()

    def test_initiate_quest(self):
        self.action_idl.state = ActionIdlenessPrototype.STATE.WAITING
        self.action_idl.percents = 0

        self.action_idl.init_quest()

        self.storage.process_turn()

        self.assertEqual(len(self.storage.actions), 2)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.QUEST)

        self.storage._test_save()

    def test_initiate_quest_just_after_quest(self):
        self.action_idl.state = ActionIdlenessPrototype.STATE.QUEST
        self.action_idl.percents = 0

        self.action_idl.init_quest()

        self.storage.process_turn()

        self.assertEqual(len(self.storage.actions), 2)
        self.assertEqual(self.storage.heroes_to_actions[self.hero.id][-1].TYPE, ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.QUEST)

        self.storage._test_save()
