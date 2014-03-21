# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.heroes.relations import HABIT_HONOR_INTERVAL

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.balance import formulas as f, constants as c, enums as e

from the_tale.game.logic import create_test_map
from the_tale.game.prototypes import TimePrototype

from the_tale.game.actions.prototypes import ActionMoveToPrototype, ActionInPlacePrototype, ActionRestPrototype
from the_tale.game.actions.prototypes import ActionResurrectPrototype, ActionBattlePvE1x1Prototype, ActionRegenerateEnergyPrototype
from the_tale.game.actions.tests.helpers import ActionEventsTestsMixin



class BaseMoveToActionTest(testcase.TestCase):

    def setUp(self):
        super(BaseMoveToActionTest, self).setUp()

        self.p1, self.p2, self.p3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]
        self.action_idl = self.hero.actions.current_action

        self.hero.position.set_place(self.p1)

        self.action_move = ActionMoveToPrototype.create(hero=self.hero, destination=self.p3)


@mock.patch('the_tale.game.balance.constants.PICKED_UP_IN_ROAD_PROBABILITY', 0)
class MoveToActionTest(BaseMoveToActionTest, ActionEventsTestsMixin):

    def setUp(self):
        super(MoveToActionTest, self).setUp()

        self.action_event = self.action_move


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_move.leader, True)
        self.assertEqual(self.action_move.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()


    def test_processed(self):
        self.hero.position.set_place(self.p3)
        self.storage.process_turn(second_step_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.storage._test_save()


    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: False)
    def test_not_ready(self):
        self.storage.process_turn(second_step_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_move)
        self.assertTrue(self.hero.position.road)
        self.storage._test_save()


    def test_full_move(self):

        current_time = TimePrototype.get_current_time()

        while self.hero.position.place is None or self.hero.position.place.id != self.p3.id:
            self.storage.process_turn(second_step_if_needed=False)
            current_time.increment_turn()

        self.assertEqual(self.hero.actions.current_action.TYPE, ActionInPlacePrototype.TYPE)
        self.storage._test_save()

    def test_full(self):

        current_time = TimePrototype.get_current_time()

        while not self.action_idl.leader:
            self.storage.process_turn(second_step_if_needed=False)
            current_time.increment_turn()

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: False)
    def test_modify_speed(self):

        with mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.modify_move_speed',
                        mock.Mock(return_value=self.hero.move_speed)) as speed_modifier_call_counter:
            self.storage.process_turn(second_step_if_needed=False)

        self.assertEqual(speed_modifier_call_counter.call_count, 1)

    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: False)
    def test_short_teleport(self):

        current_time = TimePrototype.get_current_time()

        self.storage.process_turn(second_step_if_needed=False)

        old_road_percents = self.hero.position.percents
        self.action_move.short_teleport(1)
        self.assertTrue(old_road_percents < self.hero.position.percents)

        self.action_move.short_teleport(self.hero.position.road.length)
        self.assertEqual(self.hero.position.percents, 1)
        self.assertTrue(self.action_move.updated)

        current_time.increment_turn()
        self.storage.process_turn(second_step_if_needed=False)

        self.assertEqual(self.hero.position.place.id, self.p2.id)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: False)
    def test_short_teleport__length_is_0(self):

        current_time = TimePrototype.get_current_time()

        self.action_move.length = 0

        self.storage.process_turn(second_step_if_needed=False)

        self.action_move.short_teleport(1)
        self.assertEqual(self.hero.position.percents, 1)
        self.assertEqual(self.action_move.percents, 1)
        self.assertTrue(self.action_move.updated)

        current_time.increment_turn()
        self.storage.process_turn(second_step_if_needed=False)

        self.assertEqual(self.hero.position.place.id, self.p2.id)

        self.storage._test_save()


    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: True)
    def test_battle(self):
        self.storage.process_turn(second_step_if_needed=False)
        self.assertEqual(self.hero.actions.current_action.TYPE, ActionBattlePvE1x1Prototype.TYPE)
        self.storage._test_save()


    def test_rest(self):
        self.hero.health = 1
        self.action_move.state = self.action_move.STATE.BATTLE
        self.storage.process_turn(second_step_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, ActionRestPrototype.TYPE)

        self.storage._test_save()

    def test_regenerate_energy_on_move(self):
        self.hero.preferences.set_energy_regeneration_type(e.ANGEL_ENERGY_REGENERATION_TYPES.PRAY)
        self.hero.last_energy_regeneration_at_turn -= max([f.angel_energy_regeneration_delay(energy_regeneration_type)
                                                           for energy_regeneration_type in c.ANGEL_ENERGY_REGENERATION_STEPS.keys()])
        self.action_move.state = self.action_move.STATE.CHOOSE_ROAD

        self.storage.process_turn(second_step_if_needed=False)
        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()
        self.storage.process_turn(second_step_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, ActionRegenerateEnergyPrototype.TYPE)

        self.storage._test_save()

    def test_not_regenerate_energy_on_move_for_sacrifice(self):
        self.hero.preferences.set_energy_regeneration_type(e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE)
        self.hero.last_energy_regeneration_at_turn -= max([f.angel_energy_regeneration_delay(energy_regeneration_type)
                                                           for energy_regeneration_type in c.ANGEL_ENERGY_REGENERATION_STEPS.keys()])
        self.action_move.state = self.action_move.STATE.CHOOSE_ROAD

        self.storage.process_turn(second_step_if_needed=False)
        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()
        self.storage.process_turn(second_step_if_needed=False)


        self.assertNotEqual(self.hero.actions.current_action.TYPE, ActionRegenerateEnergyPrototype.TYPE)

        self.storage._test_save()

    def test_regenerate_energy_after_battle_for_sacrifice(self):
        self.hero.preferences.set_energy_regeneration_type(e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE)
        self.hero.last_energy_regeneration_at_turn -= max([f.angel_energy_regeneration_delay(energy_regeneration_type)
                                                           for energy_regeneration_type in c.ANGEL_ENERGY_REGENERATION_STEPS.keys()])
        self.action_move.state = self.action_move.STATE.BATTLE

        self.storage.process_turn(second_step_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, ActionRegenerateEnergyPrototype.TYPE)

        self.storage._test_save()

    def test_resurrect(self):
        self.hero.kill()
        self.action_move.state = self.action_move.STATE.BATTLE
        self.storage.process_turn(second_step_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, ActionResurrectPrototype.TYPE)
        self.storage._test_save()


    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: False)
    def test_inplace(self):

        current_time = TimePrototype.get_current_time()

        self.storage.process_turn(second_step_if_needed=False)
        self.hero.position.percents = 1

        current_time.increment_turn()
        self.storage.process_turn(second_step_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, ActionInPlacePrototype.TYPE)
        self.storage._test_save()


    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: False)
    def test_stop_when_quest_required_replane(self):
        while self.action_move.state != ActionMoveToPrototype.STATE.MOVING:
            self.storage.process_turn(second_step_if_needed=False)

        with mock.patch('the_tale.game.quests.container.QuestsContainer.has_quests', True):
            self.storage.process_turn(second_step_if_needed=False)
            self.assertFalse(self.action_move.replane_required)
            self.assertEqual(self.action_move.state, ActionMoveToPrototype.STATE.MOVING)
            self.action_move.replane_required = True
            self.storage.process_turn(second_step_if_needed=False)

        self.assertEqual(self.action_move.state, ActionMoveToPrototype.STATE.PROCESSED)


    def test_hero_killed(self):
        self.hero.is_alive = False
        self.assertNotEqual(self.action_move.state, ActionMoveToPrototype.STATE.RESURRECT)
        self.storage.process_turn(second_step_if_needed=False)
        self.assertEqual(self.action_move.state, ActionMoveToPrototype.STATE.RESURRECT)

    def test_hero_need_rest(self):
        self.hero.health = 1
        self.assertNotEqual(self.action_move.state, ActionMoveToPrototype.STATE.RESTING)
        self.storage.process_turn(second_step_if_needed=False)
        self.assertEqual(self.action_move.state, ActionMoveToPrototype.STATE.RESTING)

    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: False)
    def test_move_when_real_length_is_zero(self):
        self.storage.process_turn(second_step_if_needed=False)
        self.assertEqual(self.action_move.state, ActionMoveToPrototype.STATE.MOVING)

        self.assertTrue(self.action_move.percents < 1)

        self.action_move.length = 0

        self.storage.process_turn(second_step_if_needed=False)

        self.assertEqual(self.action_move.percents, 1)


@mock.patch('the_tale.game.balance.constants.PICKED_UP_IN_ROAD_PROBABILITY', 0)
class MoveToActionWithBreaksTest(testcase.TestCase):

    def setUp(self):
        super(MoveToActionWithBreaksTest, self).setUp()
        self.p1, self.p2, self.p3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]
        self.action_idl = self.hero.actions.current_action

        self.hero.position.set_place(self.p1)

        self.action_move = ActionMoveToPrototype.create(hero=self.hero, destination=self.p3, break_at=0.75)

    def test_sequence_move(self):

        current_time = TimePrototype.get_current_time()

        while self.hero.actions.current_action != self.action_idl:
            self.storage.process_turn(second_step_if_needed=False)
            current_time.increment_turn()

        self.assertEqual(self.hero.position.road.point_1_id, self.p2.id)
        self.assertEqual(self.hero.position.road.point_2_id, self.p3.id)

        ActionMoveToPrototype.create(hero=self.hero, destination=self.p1, break_at=0.9)
        while self.hero.actions.current_action != self.action_idl:
            self.storage.process_turn(second_step_if_needed=False)
            current_time.increment_turn()

        self.assertEqual(self.hero.position.road.point_1_id, self.p1.id)
        self.assertEqual(self.hero.position.road.point_2_id, self.p2.id)

        ActionMoveToPrototype.create(hero=self.hero, destination=self.p2)
        while self.hero.position.place is None or self.hero.position.place.id != self.p2.id:
            self.storage.process_turn(second_step_if_needed=False)
            current_time.increment_turn()

        self.assertEqual(self.hero.actions.current_action.TYPE, ActionInPlacePrototype.TYPE)
        self.storage._test_save()


@mock.patch('the_tale.game.heroes.habits.Honor.interval', HABIT_HONOR_INTERVAL.RIGHT_3)
@mock.patch('the_tale.game.balance.constants.PICKED_UP_IN_ROAD_PROBABILITY', 1.01)
class MoveToActionPickedUpTest(BaseMoveToActionTest):


    @mock.patch('the_tale.game.heroes.prototypes.HeroPositionPrototype.is_battle_start_needed', lambda self: False)
    def test_short_teleport_called(self):

        self.storage.process_turn(second_step_if_needed=False)

        with mock.patch('the_tale.game.actions.prototypes.ActionMoveToPrototype.short_teleport') as short_teleport:
            self.storage.process_turn(second_step_if_needed=False)

        self.assertEqual(short_teleport.call_args_list, [mock.call(c.PICKED_UP_IN_ROAD_TELEPORT_LENGTH)])

        self.storage._test_save()
