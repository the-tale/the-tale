# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.balance import constants as c
from the_tale.game.balance import formulas as f

from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic

from the_tale.game.heroes import relations as heroes_relations

from the_tale.game.logic import create_test_map
from the_tale.game.actions import prototypes
from the_tale.game.prototypes import TimePrototype

from the_tale.game.map.relations import TERRAIN
from the_tale.game.map.storage import map_info_storage


class MoveNearActionTest(testcase.TestCase):

    def setUp(self):
        super(MoveNearActionTest, self).setUp()

        self.p1, self.p2, self.p3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]
        self.action_idl = self.hero.actions.current_action

        self.hero.position.set_place(self.p1)

        self.action_move = prototypes.ActionMoveNearPlacePrototype.create(hero=self.hero, place=self.p1, back=False)
    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_move.leader, True)
        self.assertEqual(self.action_move.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()

    def test_get_destination_coordinates(self):

        self.assertTrue(len(self.p1.nearest_cells) > 3) # two coordinates will be in coordinates set, other will not

        x_1, y_1 = self.p1.nearest_cells[0]
        map_info_storage.item.terrain[y_1][x_1] = TERRAIN.WATER_DEEP

        x_2, y_2 = self.p1.nearest_cells[1]
        map_info_storage.item.terrain[y_2][x_2] = TERRAIN.WATER_DEEP

        coordinates = set()

        for i in xrange(100):
            coordinates.add(prototypes.ActionMoveNearPlacePrototype._get_destination_coordinates(back=False, place=self.p1, terrains=(TERRAIN.WATER_DEEP,)))

        self.assertEqual(coordinates, set([(x_1, y_1), (x_2, y_2)]))


    def test_get_destination_coordinates__no_terrains(self):

        self.assertTrue(len(self.p1.nearest_cells) > 3) # two coordinates will be in coordinates set, other will not

        coordinates = set()

        for i in xrange(100):
            coordinates.add(prototypes.ActionMoveNearPlacePrototype._get_destination_coordinates(back=False, place=self.p1, terrains=(TERRAIN.WATER_DEEP,)))

        self.assertEqual(coordinates, set(self.p1.nearest_cells))

    def test_get_destination_coordinates__back(self):

        self.assertTrue(len(self.p1.nearest_cells) > 3) # two coordinates will be in coordinates set, other will not

        x_1, y_1 = self.p1.nearest_cells[0]
        map_info_storage.item.terrain[y_1][x_1] = TERRAIN.WATER_DEEP

        x_2, y_2 = self.p1.nearest_cells[1]
        map_info_storage.item.terrain[y_2][x_2] = TERRAIN.WATER_DEEP

        coordinates = set()

        for i in xrange(100):
            coordinates.add(prototypes.ActionMoveNearPlacePrototype._get_destination_coordinates(back=True, place=self.p1, terrains=(TERRAIN.WATER_DEEP,)))

        self.assertEqual(coordinates, set([(self.p1.x, self.p1.y)]))


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_processed(self):

        current_time = TimePrototype.get_current_time()

        self.storage.process_turn(continue_steps_if_needed=False)

        x, y = self.action_move.get_destination()
        self.hero.position.set_coordinates(x, y, x, y, percents=1)

        current_time.increment_turn()
        self.storage.process_turn(continue_steps_if_needed=False)

        # can end in field or in start place
        self.assertTrue(self.hero.actions.current_action.TYPE in [prototypes.ActionIdlenessPrototype.TYPE, prototypes.ActionInPlacePrototype.TYPE])
        self.assertTrue(self.hero.position.is_walking or self.hero.position.place)

        self.storage._test_save()


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_not_ready(self):
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_move)
        self.assertTrue(self.hero.position.is_walking or self.hero.position.place) # can end in start place
        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.position.Position.subroad_len', lambda self: 1)
    def test_modify_speed(self):

        with mock.patch('the_tale.game.heroes.objects.Hero.modify_move_speed',
                        mock.Mock(return_value=self.hero.move_speed)) as speed_modifier_call_counter:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(speed_modifier_call_counter.call_count, 1)

    def test_full_move_and_back(self):

        current_time = TimePrototype.get_current_time()

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)
            current_time.increment_turn()

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionIdlenessPrototype.TYPE)
        self.assertTrue(self.hero.position.is_walking or self.hero.position.place)  # can end in start place

        prototypes.ActionMoveNearPlacePrototype.create(hero=self.hero, place=self.p1, back=True)
        while self.hero.position.place is None or self.hero.position.place.id != self.p1.id:
            self.storage.process_turn(continue_steps_if_needed=False)
            current_time.increment_turn()

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)
        self.assertTrue(not self.hero.position.is_walking)
        self.storage._test_save()

    def test_move_change_place_coordinates_and_back(self):

        current_time = TimePrototype.get_current_time()

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)
            current_time.increment_turn()

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionIdlenessPrototype.TYPE)
        self.assertTrue(self.hero.position.is_walking or self.hero.position.place)  # can end in start place

        prototypes.ActionMoveNearPlacePrototype.create(hero=self.hero, place=self.p1, back=True)
        self.p1._model.x = self.p1.x + 1
        self.p1._model.y = self.p1.y + 1
        self.p1.save()

        while self.hero.position.place is None or self.hero.position.place.id != self.p1.id:
            self.storage.process_turn(continue_steps_if_needed=False)
            current_time.increment_turn()

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)
        self.assertTrue(not self.hero.position.is_walking)
        self.storage._test_save()

    def test_full(self):

        current_time = TimePrototype.get_current_time()

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)
            current_time.increment_turn()

        self.assertTrue(self.action_idl.leader)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: True)
    def test_battle(self):
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionBattlePvE1x1Prototype.TYPE)
        self.storage._test_save()

    def test_regenerate_energy_on_move(self):
        self.hero.preferences.set_energy_regeneration_type(heroes_relations.ENERGY_REGENERATION.PRAY)
        self.hero.last_energy_regeneration_at_turn -= max(zip(*heroes_relations.ENERGY_REGENERATION.select('period'))[0])
        self.action_move.state = self.action_move.STATE.MOVING

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionRegenerateEnergyPrototype.TYPE)

        self.storage._test_save()

    def test_not_regenerate_energy_on_move_for_sacrifice(self):
        self.hero.preferences.set_energy_regeneration_type(heroes_relations.ENERGY_REGENERATION.SACRIFICE)
        self.hero.last_energy_regeneration_at_turn -= max(zip(*heroes_relations.ENERGY_REGENERATION.select('period'))[0])
        self.action_move.state = self.action_move.STATE.MOVING

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertNotEqual(self.hero.actions.current_action.TYPE, prototypes.ActionRegenerateEnergyPrototype.TYPE)

        self.storage._test_save()


    def test_regenerate_energy_after_battle_for_sacrifice(self):
        self.hero.preferences.set_energy_regeneration_type(heroes_relations.ENERGY_REGENERATION.SACRIFICE)
        self.hero.last_energy_regeneration_at_turn -= max(zip(*heroes_relations.ENERGY_REGENERATION.select('period'))[0])
        self.action_move.state = self.action_move.STATE.BATTLE

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionRegenerateEnergyPrototype.TYPE)

        self.storage._test_save()


    def test_rest(self):
        self.hero.health = 1
        self.action_move.state = self.action_move.STATE.BATTLE
        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionRestPrototype.TYPE)
        self.storage._test_save()


    @mock.patch('the_tale.game.companions.objects.Companion.need_heal', True)
    def test_heal_companion(self):

        self.action_move.state = self.action_move.STATE.BATTLE

        companion_record = companions_storage.companions.enabled_companions().next()
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionMoveNearPlacePrototype.TYPE)

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionHealCompanionPrototype.TYPE)
        self.assertEqual(self.action_move.state, prototypes.ActionMoveNearPlacePrototype.STATE.HEALING_COMPANION)

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionMoveNearPlacePrototype.TYPE)
        self.assertEqual(self.hero.actions.current_action.state, prototypes.ActionMoveNearPlacePrototype.STATE.HEALING_COMPANION)


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.can_companion_say_wisdom', lambda hero: True)
    @mock.patch('the_tale.game.balance.constants.COMPANIONS_EXP_PER_MOVE_PROBABILITY', 1.0)
    def test_companion_say_wisdom(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)

        with self.check_delta(lambda: self.hero.experience, c.COMPANIONS_EXP_PER_MOVE_GET_EXP):
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertTrue(self.hero.journal.messages[-1].key.is_COMPANIONS_SAY_WISDOM)

        self.storage._test_save()


    def test_resurrect(self):
        self.hero.kill()
        self.action_move.state = self.action_move.STATE.BATTLE
        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionResurrectPrototype.TYPE)
        self.storage._test_save()


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_stop_when_quest_required_replane(self):
        while self.action_move.state != prototypes.ActionMoveNearPlacePrototype.STATE.MOVING:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertFalse(self.action_move.replane_required)
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.action_move.state, prototypes.ActionMoveNearPlacePrototype.STATE.MOVING)
        self.action_move.replane_required = True
        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, prototypes.ActionMoveNearPlacePrototype.STATE.PROCESSED)
