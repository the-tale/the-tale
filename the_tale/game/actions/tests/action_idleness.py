# coding: utf-8

from common.utils import testcase

from accounts.logic import register_user

from game.balance import constants as c, formulas as f, enums as e
from game.prototypes import TimePrototype

from game.logic_storage import LogicStorage
from game.logic import create_test_map

from game.heroes.prototypes import HeroPrototype
from game.abilities.relations import HELP_CHOICES

from game.actions.prototypes import ActionIdlenessPrototype, ActionQuestPrototype, ActionInPlacePrototype, ActionRegenerateEnergyPrototype, E

class IdlenessActionTest(testcase.TestCase):

    def setUp(self):
        super(IdlenessActionTest, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.hero.actions.current_action

    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, True)
        self.storage._test_save()


    def test_first_quest(self):
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.QUEST)
        self.assertTrue(self.action_idl.bundle_id is not None)
        self.storage._test_save()


    def test_inplace(self):
        self.action_idl.state = ActionIdlenessPrototype.STATE.QUEST
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, ActionInPlacePrototype.TYPE)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.IN_PLACE)
        self.storage._test_save()

    def test_waiting(self):
        self.action_idl.state = ActionIdlenessPrototype.STATE.IN_PLACE
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.WAITING)
        self.storage._test_save()

    def test_regenerate_energy_action_create(self):
        self.hero.preferences.energy_regeneration_type = e.ANGEL_ENERGY_REGENERATION_TYPES.PRAY
        self.hero.last_energy_regeneration_at_turn -= max([f.angel_energy_regeneration_delay(energy_regeneration_type)
                                                           for energy_regeneration_type in c.ANGEL_ENERGY_REGENERATION_STEPS.keys()])
        self.action_idl.percents = 0.0
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, ActionRegenerateEnergyPrototype.TYPE)
        self.storage._test_save()

    def test_regenerate_energy_action_not_create_for_sacrifice(self):
        self.action_idl.percents = 0
        self.hero.preferences.energy_regeneration_type = e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE
        self.hero.last_energy_regeneration_at_turn -= max([f.angel_energy_regeneration_delay(energy_regeneration_type)
                                                           for energy_regeneration_type in c.ANGEL_ENERGY_REGENERATION_STEPS.keys()])
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.storage._test_save()


    def test_full_waiting(self):
        self.action_idl.state = ActionIdlenessPrototype.STATE.WAITING
        self.action_idl.percents = 0

        current_time = TimePrototype.get_current_time()

        for i in xrange(c.TURNS_TO_IDLE*self.hero.level):
            self.storage.process_turn()
            current_time.increment_turn()
            self.assertEqual(len(self.hero.actions.actions_list), 1)
            self.assertEqual(self.hero.actions.current_action, self.action_idl)

        self.storage.process_turn()

        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.QUEST)

        self.storage._test_save()

    def test_initiate_quest(self):
        self.action_idl.state = ActionIdlenessPrototype.STATE.WAITING
        self.action_idl.percents = 0

        self.action_idl.init_quest()

        self.storage.process_turn()

        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.QUEST)

        self.storage._test_save()

    def test_initiate_quest_just_after_quest(self):
        self.action_idl.state = ActionIdlenessPrototype.STATE.QUEST
        self.action_idl.percents = 0

        self.action_idl.init_quest()

        self.storage.process_turn()

        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, ActionIdlenessPrototype.STATE.QUEST)

        self.storage._test_save()

    def test_help_choices__contain_start_quest(self):
        self.action_idl.percents = 0.0
        self.assertTrue(HELP_CHOICES.START_QUEST in self.action_idl.HELP_CHOICES)

    def test_help_choices__start_quest_removed(self):
        self.action_idl.percents = 1.0
        self.assertFalse(HELP_CHOICES.START_QUEST in self.action_idl.HELP_CHOICES)
