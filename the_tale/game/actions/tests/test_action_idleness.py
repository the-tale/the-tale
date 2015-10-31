# coding: utf-8

import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.balance import constants as c, formulas as f
from the_tale.game.prototypes import TimePrototype

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map

from the_tale.game.abilities.relations import HELP_CHOICES

from the_tale.game.map.roads.storage import roads_storage
from the_tale.game.heroes import relations as heroes_relations

from the_tale.game.actions import prototypes


class IdlenessActionTest(testcase.TestCase):

    def setUp(self):
        super(IdlenessActionTest, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.action_idl = self.hero.actions.current_action

    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, True)
        self.assertEqual(self.action_idl.percents, 1.0)
        self.storage._test_save()


    def test_first_quest(self):
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, prototypes.ActionIdlenessPrototype.STATE.QUEST)
        self.assertEqual(self.action_idl.bundle_id, self.hero.account_id)
        self.storage._test_save()


    def test_reset_percents_on_quest_end(self):
        self.action_idl.percents = 1.0
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.QUEST
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.action_idl.percents, 0.0)


    def test_inplace(self):
        self.action_idl.percents = 1.0
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.QUEST
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)
        self.assertEqual(self.action_idl.state, prototypes.ActionIdlenessPrototype.STATE.IN_PLACE)
        self.storage._test_save()

    def test_waiting(self):
        self.action_idl.percents = 0.0
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.IN_PLACE
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.assertEqual(self.action_idl.state, prototypes.ActionIdlenessPrototype.STATE.WAITING)
        self.storage._test_save()

    def test_regenerate_energy_action_create(self):
        self.hero.preferences.set_energy_regeneration_type(heroes_relations.ENERGY_REGENERATION.PRAY)
        self.hero.last_energy_regeneration_at_turn -= max(zip(*heroes_relations.ENERGY_REGENERATION.select('period'))[0])
        self.action_idl.percents = 0.0
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionRegenerateEnergyPrototype.TYPE)
        self.storage._test_save()

    def test_regenerate_energy_action_not_create_for_sacrifice(self):
        self.action_idl.percents = 0
        self.hero.preferences.set_energy_regeneration_type(heroes_relations.ENERGY_REGENERATION.SACRIFICE)
        self.hero.last_energy_regeneration_at_turn -= max(zip(*heroes_relations.ENERGY_REGENERATION.select('period'))[0])
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.storage._test_save()


    def test_full_waiting(self):
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.WAITING
        self.action_idl.percents = 0

        current_time = TimePrototype.get_current_time()

        for i in xrange(c.TURNS_TO_IDLE*self.hero.level):
            self.storage.process_turn()
            current_time.increment_turn()
            self.assertEqual(len(self.hero.actions.actions_list), 1)
            self.assertEqual(self.hero.actions.current_action, self.action_idl)

        self.storage.process_turn()

        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, prototypes.ActionIdlenessPrototype.STATE.QUEST)

        self.storage._test_save()

    def test_initiate_quest(self):
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.WAITING
        self.action_idl.percents = 0

        self.action_idl.init_quest()

        self.storage.process_turn()

        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, prototypes.ActionIdlenessPrototype.STATE.QUEST)

        self.storage._test_save()

    def test_initiate_quest_just_after_quest(self):
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.QUEST
        self.action_idl.percents = 0

        self.action_idl.init_quest()

        self.storage.process_turn()

        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, prototypes.ActionIdlenessPrototype.STATE.QUEST)

        self.storage._test_save()

    def test_help_choices__contain_start_quest(self):
        self.action_idl.percents = 0.0
        self.assertTrue(HELP_CHOICES.START_QUEST in self.action_idl.HELP_CHOICES)

    def test_help_choices__start_quest_removed(self):
        self.action_idl.percents = 1.0
        self.assertFalse(HELP_CHOICES.START_QUEST in self.action_idl.HELP_CHOICES)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_return_from_road__after_quest(self):
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.QUEST
        self.hero.position.set_road(list(roads_storage.all())[0], percents=0.5)
        self.storage.process_turn()
        self.assertEqual(self.hero.actions.number, 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionMoveToPrototype.TYPE)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_return_from_wild_terrain__after_quest(self):
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.QUEST
        self.hero.position.set_coordinates(0, 0, 5, 5, percents=0)
        self.storage.process_turn()
        self.assertEqual(self.hero.actions.number, 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionMoveNearPlacePrototype.TYPE)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_return_from_road__after_resurrect(self):
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.RESURRECT
        self.hero.position.set_road(list(roads_storage.all())[0], percents=0.5)
        self.storage.process_turn()
        self.assertEqual(self.hero.actions.number, 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionMoveToPrototype.TYPE)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_return_from_wild_terrain__after_resurrect(self):
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.RESURRECT
        self.hero.position.set_coordinates(0, 0, 5, 5, percents=0)
        self.storage.process_turn()
        self.assertEqual(self.hero.actions.number, 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionMoveNearPlacePrototype.TYPE)

    def test_resurrect(self):
        self.hero.is_alive = False
        self.storage.process_turn()
        self.assertEqual(self.hero.actions.number, 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionResurrectPrototype.TYPE)
