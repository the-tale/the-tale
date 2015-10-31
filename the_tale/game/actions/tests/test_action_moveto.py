# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.relations import HABIT_HONOR_INTERVAL

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.balance import formulas as f, constants as c

from the_tale.game.companions import storage as companions_storage
from the_tale.game.companions import logic as companions_logic

from the_tale.game.heroes import relations as heroes_relations

from the_tale.game.logic import create_test_map
from the_tale.game.prototypes import TimePrototype

from the_tale.game.abilities.relations import HELP_CHOICES

from the_tale.game.actions import prototypes
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

        self.action_move = prototypes.ActionMoveToPrototype.create(hero=self.hero, destination=self.p3)


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


    def test_help_choices(self):
        self.assertNotEqual(self.action_move.state, self.action_move.STATE.MOVING)

        self.assertFalse(HELP_CHOICES.TELEPORT in self.action_move.HELP_CHOICES)

        self.action_move.state = self.action_move.STATE.MOVING

        self.assertTrue(HELP_CHOICES.TELEPORT in self.action_move.HELP_CHOICES)


    def test_processed(self):
        self.hero.position.set_place(self.p3)
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.storage._test_save()


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_not_ready(self):
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action, self.action_move)
        self.assertTrue(self.hero.position.road)
        self.storage._test_save()


    def test_full_move(self):

        current_time = TimePrototype.get_current_time()

        while self.hero.position.place is None or self.hero.position.place.id != self.p3.id:
            self.storage.process_turn(continue_steps_if_needed=False)
            current_time.increment_turn()

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)
        self.storage._test_save()

    def test_full(self):

        current_time = TimePrototype.get_current_time()

        while not self.action_idl.leader:
            self.storage.process_turn(continue_steps_if_needed=False)
            current_time.increment_turn()

        self.storage._test_save()


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_modify_speed(self):

        with mock.patch('the_tale.game.heroes.objects.Hero.modify_move_speed',
                        mock.Mock(return_value=self.hero.move_speed)) as speed_modifier_call_counter:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(speed_modifier_call_counter.call_count, 1)


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_fly_probability', 1.0)
    def test_teleport_by_flying_companion(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)

        with self.check_increased(lambda: self.action_move.percents):
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertTrue(self.hero.journal.messages[-1].key.is_COMPANIONS_FLY)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_teleport_probability', 1.0)
    def test_teleport_by_teleportator_companion(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.assertEqual(self.action_move.state, self.action_move.STATE.CHOOSE_ROAD)

        with self.check_increased(lambda: self.action_move.percents):
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)

        self.assertTrue(any(message.key.is_COMPANIONS_TELEPORT for message in self.hero.journal.messages if message.key is not None))


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_teleport_probability', 1.0)
    def test_teleport_by_teleportator_companion__not_moving_state(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.assertEqual(self.action_move.state, self.action_move.STATE.CHOOSE_ROAD)
        self.hero.position.set_place(self.p3) # hero in destination

        with self.check_not_changed(lambda: self.action_move.percents):
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.PROCESSED)

        self.assertFalse(self.hero.journal.messages[-1].key.is_COMPANIONS_TELEPORT)


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport(self):

        self.storage.process_turn(continue_steps_if_needed=False)

        old_road_percents = self.hero.position.percents
        self.action_move.teleport(1, create_inplace_action=True)
        self.assertTrue(old_road_percents < self.hero.position.percents)

        self.action_move.teleport(self.hero.position.road.length, create_inplace_action=True)
        self.assertEqual(self.hero.position.place.id, self.p2.id)
        self.assertTrue(self.action_move.updated)

        self.storage._test_save()


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_place(self):

        self.storage.process_turn(continue_steps_if_needed=False)

        self.action_move.teleport_to_place(create_inplace_action=True)
        self.assertEqual(self.hero.position.place.id, self.p2.id)

        self.assertFalse(self.action_move.leader)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_end(self):
        current_time = TimePrototype.get_current_time()

        self.storage.process_turn(continue_steps_if_needed=False)

        self.action_move.teleport_to_end()
        self.assertEqual(self.hero.position.place.id, self.p3.id)
        self.assertTrue(self.action_move.updated)

        self.assertFalse(self.action_move.leader)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)

        current_time.increment_turn()
        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.position.place.id, self.p3.id)

        self.storage._test_save()


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport__length_is_0(self):

        current_time = TimePrototype.get_current_time()

        self.storage.process_turn(continue_steps_if_needed=False)

        self.action_move.length = 0
        self.action_move.percents = 1
        self.hero.position.percents = 1

        with self.check_not_changed(lambda: self.action_move.percents):
            self.action_move.teleport(1, create_inplace_action=True)

        self.assertEqual(self.action_move.state, self.action_move.STATE.PROCESSED)

        self.assertTrue(self.action_move.updated)

        current_time.increment_turn()

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.position.place.id, self.p2.id)

        self.storage._test_save()


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: True)
    def test_battle(self):
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionBattlePvE1x1Prototype.TYPE)
        self.storage._test_save()


    def test_rest(self):
        self.hero.health = 1
        self.action_move.state = self.action_move.STATE.BATTLE
        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionRestPrototype.TYPE)

        self.storage._test_save()

    def test_regenerate_energy_on_move(self):
        self.hero.preferences.set_energy_regeneration_type(heroes_relations.ENERGY_REGENERATION.PRAY)
        self.hero.last_energy_regeneration_at_turn -= max(zip(*heroes_relations.ENERGY_REGENERATION.select('period'))[0])
        self.action_move.state = self.action_move.STATE.CHOOSE_ROAD

        self.storage.process_turn(continue_steps_if_needed=False)
        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()
        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionRegenerateEnergyPrototype.TYPE)

        self.storage._test_save()

    def test_not_regenerate_energy_on_move_for_sacrifice(self):
        self.hero.preferences.set_energy_regeneration_type(heroes_relations.ENERGY_REGENERATION.SACRIFICE)
        self.hero.last_energy_regeneration_at_turn -= max(zip(*heroes_relations.ENERGY_REGENERATION.select('period'))[0])
        self.action_move.state = self.action_move.STATE.CHOOSE_ROAD

        self.storage.process_turn(continue_steps_if_needed=False)
        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()
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

    def test_resurrect(self):
        self.hero.kill()
        self.action_move.state = self.action_move.STATE.BATTLE
        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionResurrectPrototype.TYPE)
        self.storage._test_save()


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_inplace(self):

        current_time = TimePrototype.get_current_time()

        self.storage.process_turn(continue_steps_if_needed=False)
        self.hero.position.percents = 1

        current_time.increment_turn()
        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)
        self.storage._test_save()


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_stop_when_quest_required_replane(self):
        while self.action_move.state != prototypes.ActionMoveToPrototype.STATE.MOVING:
            self.storage.process_turn(continue_steps_if_needed=False)

        with mock.patch('the_tale.game.quests.container.QuestsContainer.has_quests', True):
            self.storage.process_turn(continue_steps_if_needed=False)
            self.assertFalse(self.action_move.replane_required)
            self.assertEqual(self.action_move.state, prototypes.ActionMoveToPrototype.STATE.MOVING)
            self.action_move.replane_required = True
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, prototypes.ActionMoveToPrototype.STATE.PROCESSED)


    def test_hero_killed(self):
        self.hero.is_alive = False
        self.assertNotEqual(self.action_move.state, prototypes.ActionMoveToPrototype.STATE.RESURRECT)
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.action_move.state, prototypes.ActionMoveToPrototype.STATE.RESURRECT)

    def test_hero_need_rest(self):
        self.hero.health = 1
        self.assertNotEqual(self.action_move.state, prototypes.ActionMoveToPrototype.STATE.RESTING)
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.action_move.state, prototypes.ActionMoveToPrototype.STATE.RESTING)

    @mock.patch('the_tale.game.companions.objects.Companion.need_heal', True)
    def test_hero_need_heal_companion(self):
        companion_record = companions_storage.companions.enabled_companions().next()
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionMoveToPrototype.TYPE)

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionHealCompanionPrototype.TYPE)
        self.assertEqual(self.action_move.state, prototypes.ActionMoveToPrototype.STATE.HEALING_COMPANION)

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionMoveToPrototype.TYPE)
        self.assertEqual(self.hero.actions.current_action.state, prototypes.ActionMoveToPrototype.STATE.HEALING_COMPANION)


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.companions.objects.Companion.need_heal', True)
    def test_hero_need_heal_companion__battle(self):
        self.action_move.state = self.action_move.STATE.BATTLE

        companion_record = companions_storage.companions.enabled_companions().next()
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionMoveToPrototype.TYPE)

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionHealCompanionPrototype.TYPE)
        self.assertEqual(self.action_move.state, prototypes.ActionMoveToPrototype.STATE.HEALING_COMPANION)

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionMoveToPrototype.TYPE)
        self.assertEqual(self.hero.actions.current_action.state, prototypes.ActionMoveToPrototype.STATE.HEALING_COMPANION)


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_move_when_real_length_is_zero(self):
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.action_move.state, prototypes.ActionMoveToPrototype.STATE.MOVING)

        self.assertTrue(self.action_move.percents < 1)

        self.action_move.length = 0

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.percents, 1)


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



@mock.patch('the_tale.game.balance.constants.PICKED_UP_IN_ROAD_PROBABILITY', 0)
class MoveToActionWithBreaksTest(testcase.TestCase):

    FIRST_BREAK_AT = 0.75

    def setUp(self):
        super(MoveToActionWithBreaksTest, self).setUp()
        self.p1, self.p2, self.p3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]
        self.action_idl = self.hero.actions.current_action

        self.hero.position.set_place(self.p1)

        self.action_move = prototypes.ActionMoveToPrototype.create(hero=self.hero, destination=self.p3, break_at=self.FIRST_BREAK_AT)

    def test_sequence_move(self):

        current_time = TimePrototype.get_current_time()

        while self.hero.actions.current_action != self.action_idl:
            self.storage.process_turn(continue_steps_if_needed=False)
            current_time.increment_turn()

        self.assertEqual(self.hero.position.road.point_1_id, self.p2.id)
        self.assertEqual(self.hero.position.road.point_2_id, self.p3.id)

        real_percents = None

        prototypes.ActionMoveToPrototype.create(hero=self.hero, destination=self.p1, break_at=0.9)
        while self.hero.actions.current_action != self.action_idl:
            real_percents = self.hero.actions.current_action.percents
            self.storage.process_turn(continue_steps_if_needed=False)
            current_time.increment_turn()

        self.assertEqual(round(real_percents, 1), 0.9)

        self.assertEqual(self.hero.position.road.point_1_id, self.p1.id)
        self.assertEqual(self.hero.position.road.point_2_id, self.p2.id)

        prototypes.ActionMoveToPrototype.create(hero=self.hero, destination=self.p2)
        while self.hero.position.place is None or self.hero.position.place.id != self.p2.id:
            self.storage.process_turn(continue_steps_if_needed=False)
            current_time.increment_turn()

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)
        self.storage._test_save()


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_place__break_at(self):

        self.storage.process_turn(continue_steps_if_needed=False)

        self.action_move.teleport_to_place(create_inplace_action=True)

        self.assertEqual(self.hero.position.place.id, self.p2.id)

        while not self.hero.actions.current_action.TYPE.is_MOVE_TO:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertTrue(self.action_move.teleport_to_place(create_inplace_action=True))

        self.assertNotEqual(self.hero.position.road, None)
        self.assertTrue(self.hero.position.percents < 1)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_MOVE_TO)
        self.assertEqual(self.hero.actions.current_action.percents, self.FIRST_BREAK_AT)

        self.assertTrue(self.action_move.leader)

        self.assertEqual(self.hero.position.place, None)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_end__break_at(self):

        self.storage.process_turn(continue_steps_if_needed=False)

        self.action_move.teleport_to_end()

        self.assertNotEqual(self.hero.position.road, None)
        self.assertTrue(self.hero.position.percents < 1.0)

        self.assertEqual(self.p2.id, self.hero.position.road.point_1_id)
        self.assertEqual(self.p3.id, self.hero.position.road.point_2_id)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_MOVE_TO)
        self.assertEqual(self.hero.actions.current_action.percents, self.FIRST_BREAK_AT)

        self.assertTrue(self.action_move.leader)

        self.storage._test_save()



@mock.patch('the_tale.game.heroes.habits.Honor.interval', HABIT_HONOR_INTERVAL.RIGHT_3)
@mock.patch('the_tale.game.balance.constants.PICKED_UP_IN_ROAD_PROBABILITY', 1.01)
class MoveToActionPickedUpTest(BaseMoveToActionTest):


    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_called(self):

        self.storage.process_turn(continue_steps_if_needed=False)

        with mock.patch('the_tale.game.actions.prototypes.ActionMoveToPrototype.teleport') as teleport:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(teleport.call_args_list, [mock.call(c.PICKED_UP_IN_ROAD_TELEPORT_LENGTH, create_inplace_action=True)])

        self.storage._test_save()
