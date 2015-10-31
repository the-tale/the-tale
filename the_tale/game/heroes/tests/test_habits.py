# coding: utf-8

import contextlib

import mock

from questgen.relations import OPTION_MARKERS as QUEST_OPTION_MARKERS

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user
from the_tale.accounts.achievements.relations import ACHIEVEMENT_TYPE

from the_tale.game.actions.fake import FakeActor
from the_tale.game.actions.relations import ACTION_EVENT

from the_tale.game.balance import constants as c
from the_tale.game.logic import create_test_map
from the_tale.game import relations as game_relations
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.heroes.relations import MODIFIERS
from the_tale.game.heroes import habits


class BaseHabitTest(testcase.TestCase):

    ALL_QUEST_MARKERS = set([QUEST_OPTION_MARKERS.DISHONORABLE,
                             QUEST_OPTION_MARKERS.HONORABLE,
                             QUEST_OPTION_MARKERS.AGGRESSIVE,
                             QUEST_OPTION_MARKERS.UNAGGRESSIVE])


    def setUp(self):
        super(BaseHabitTest, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]


    def check_crit_chance_equal(self, mob, expected_crit_chance):
        self.actor_hero.context._on_every_turn()
        self.hero.update_context(self.actor_hero, mob)
        self.assertEqual(round(self.actor_hero.context.crit_chance, 5), expected_crit_chance)

    def check_first_strike(self, mob, expected_first_strike):
        self.actor_hero.context._on_every_turn()
        self.hero.update_context(self.actor_hero, mob)
        self.assertEqual(self.actor_hero.context.first_strike, expected_first_strike)

    def check_quest_markers(self, expected_markers, habit_class):
        with mock.patch.object(habit_class, 'raw_value', c.HABITS_BORDER):
            self.assertEqual(self.hero.prefered_quest_markers(), set(expected_markers))

        with mock.patch.object(habit_class, 'raw_value', -c.HABITS_BORDER):
            self.assertEqual(self.hero.prefered_quest_markers(), set(expected_markers))


        no_markers = False
        markers = set()

        with mock.patch.object(habit_class, 'raw_value', c.HABITS_BORDER / 2):
            for i in xrange(100):
                current_markers = self.hero.prefered_quest_markers()
                if current_markers:
                    markers |= current_markers
                else:
                    no_markers = True


        self.assertEqual(markers, set(expected_markers))
        self.assertTrue(no_markers)

        no_markers = False
        markers = set()

        with mock.patch.object(habit_class, 'raw_value', -c.HABITS_BORDER / 2):
            for i in xrange(100):
                current_markers = self.hero.prefered_quest_markers()
                if current_markers:
                    markers |= current_markers
                else:
                    no_markers = True

        self.assertEqual(markers, set(expected_markers))
        self.assertTrue(no_markers)

        with mock.patch.object(habit_class, 'raw_value', 0):
            self.assertEqual(self.hero.prefered_quest_markers(), set())

    def check_quest_markers_reward_bonus(self, expected_markers, habit_class):
        with mock.patch.object(habit_class, 'raw_value', c.HABITS_BORDER / 2):
            markers = self.hero.quest_markers_rewards_bonus()

            for quest_marker in self.ALL_QUEST_MARKERS:
                if quest_marker in expected_markers:
                    self.assertTrue(markers[quest_marker] > 0)
                else:
                    self.assertFalse(quest_marker in markers)



class HabitTest(BaseHabitTest):

    def test_raw_value(self):
        self.assertEqual(self.hero.habit_honor.raw_value, 0)

        self.hero.habit_honor.raw_value = 500
        self.assertEqual(self.hero.habit_honor.raw_value, 500)

    def test_achievements__honor(self):
        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.habit_honor.change(-500)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.HABITS_HONOR,
                                                                        old_value=0,
                                                                        new_value=-500)])

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.habit_honor.change(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.HABITS_HONOR,
                                                                        old_value=-500,
                                                                        new_value=166)])

    def test_achievements__peacefulness(self):
        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.habit_peacefulness.change(-500)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.HABITS_PEACEFULNESS,
                                                                        old_value=0,
                                                                        new_value=-500)])

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.habit_peacefulness.change(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.HABITS_PEACEFULNESS,
                                                                        old_value=-500,
                                                                        new_value=166)])

    def test_verbose_value(self):
        values = set()

        self.hero.habit_honor.change(-500)

        for gender in game_relations.GENDER.records:
            self.hero.gender = gender
            values.add(self.hero.habit_honor.verbose_value)

        self.assertEqual(len(values), 3)

        self.hero.habit_honor.change(600)

        for gender in game_relations.GENDER.records:
            self.hero.gender = gender
            values.add(self.hero.habit_honor.verbose_value)

        self.assertEqual(len(values), 6)


    def test_interval_and_change(self):
        self.assertTrue(self.hero.habit_honor.interval.is_NEUTRAL)
        for expected_interval, right_border in zip(self.hero.habit_honor.TYPE.intervals.records, c.HABITS_RIGHT_BORDERS):
            self.hero.habit_honor.change(right_border - self.hero.habit_honor.raw_value - 0.01)
            self.assertEqual(self.hero.habit_honor.interval, expected_interval)

    @mock.patch('the_tale.game.heroes.objects.Hero.habits_increase_modifier', 2)
    @mock.patch('the_tale.game.heroes.objects.Hero.habits_decrease_modifier', 0.5)
    def test_change_speed(self):
        self.hero.habit_honor.change(1)
        self.assertEqual(self.hero.habit_honor.raw_value, 1)

        self.hero.habit_honor.change(1)
        self.assertEqual(self.hero.habit_honor.raw_value, 3)

        self.hero.habit_honor.change(-8)
        self.assertEqual(self.hero.habit_honor.raw_value, -1)

        self.hero.habit_honor.change(-1)
        self.assertEqual(self.hero.habit_honor.raw_value, -3)

        self.hero.habit_honor.change(6)
        self.assertEqual(self.hero.habit_honor.raw_value, 0)

    def test_real_interval(self):
        self.assertTrue(self.hero.habit_honor.interval.is_NEUTRAL)
        for expected_interval, right_border in zip(self.hero.habit_honor.TYPE.intervals.records, c.HABITS_RIGHT_BORDERS):
            self.hero.habit_honor.change(right_border - self.hero.habit_honor.raw_value - 0.01)
            self.assertEqual(self.hero.habit_honor._real_interval, expected_interval)

    @mock.patch('the_tale.game.heroes.objects.Hero.clouded_mind', True)
    def test_real_interval__clouded_mind(self):
        self.assertTrue(self.hero.habit_honor.interval.is_NEUTRAL)
        intervals = set()

        for i in xrange(100):
            intervals.add(self.hero.habit_honor._real_interval)

        self.assertEqual(intervals, set(game_relations.HABIT_HONOR_INTERVAL.records))

    def test_reset_accessories_cache_on_change(self):
        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.hero.habit_honor.change(-500)

        self.assertEqual(reset_accessors_cache.call_count, 1)


class UpdateHabitsTest(BaseHabitTest):

    def setUp(self):
        super(UpdateHabitsTest, self).setUp()

        self.hero.habit_honor.change(500)
        self.hero.habit_peacefulness.change(-500)


    @contextlib.contextmanager
    def check_habits_changed(self, d_honor, d_peacefulness):
        with self.check_delta(lambda: self.hero.habit_honor.raw_value, d_honor):
            with self.check_delta(lambda: self.hero.habit_peacefulness.raw_value, d_peacefulness):
                yield


    def test_correlation_requirements__none(self):
        with self.check_habits_changed(-1, 1):
            self.hero.update_habits(mock.Mock(correlation_requirements=None, honor=-1, peacefulness=1))

        with self.check_habits_changed(2, -2):
            self.hero.update_habits(mock.Mock(correlation_requirements=None, honor=2, peacefulness=-2))


    def test_correlation_requirements__true(self):
        with self.check_habits_changed(0, 0):
            self.hero.update_habits(mock.Mock(correlation_requirements=True, honor=-1, peacefulness=1))

        with self.check_habits_changed(2, -2):
            self.hero.update_habits(mock.Mock(correlation_requirements=True, honor=2, peacefulness=-2))


    def test_correlation_requirements__false(self):
        with self.check_habits_changed(-1, 1):
            self.hero.update_habits(mock.Mock(correlation_requirements=False, honor=-1, peacefulness=1))

        with self.check_habits_changed(0, 0):
            self.hero.update_habits(mock.Mock(correlation_requirements=False, honor=2, peacefulness=-2))


@mock.patch('the_tale.game.balance.constants.KILL_BEFORE_BATTLE_PROBABILITY', 1.01)
@mock.patch('the_tale.game.balance.constants.PICKED_UP_IN_ROAD_PROBABILITY', 1.01)
@mock.patch('the_tale.game.mobs.storage.mobs_storage.mob_type_fraction', lambda mob_type: {game_relations.BEING_TYPE.PLANT: 0.1,
                                                                                           game_relations.BEING_TYPE.CIVILIZED: 0.4,
                                                                                           game_relations.BEING_TYPE.MONSTER: 0.5}.get(mob_type, 0))
class HonorHabitModifiersTest(BaseHabitTest):

    def setUp(self):
        super(HonorHabitModifiersTest, self).setUp()

        self.actor_hero = FakeActor(name='attacker')

        self.mob_neutral = FakeActor(name='defender', mob_type=game_relations.BEING_TYPE.PLANT)

        self.mob_civilized = FakeActor(name='defender', mob_type=game_relations.BEING_TYPE.CIVILIZED)
        self.mob_monster = FakeActor(name='defender', mob_type=game_relations.BEING_TYPE.MONSTER)

    @mock.patch('the_tale.game.heroes.habits.Honor.interval', game_relations.HABIT_HONOR_INTERVAL.LEFT_3)
    def test_left_3(self):
        self.assertTrue(self.hero.check_attribute(MODIFIERS.KILL_BEFORE_BATTLE))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PICKED_UP_IN_ROAD))

        self.assertTrue(self.hero.modify_attribute(MODIFIERS.POWER_TO_ENEMY, 1.0) > 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_FRIEND, 1.0), 1.0)

        self.check_crit_chance_equal(self.mob_neutral, 0.0)
        self.check_crit_chance_equal(self.mob_civilized, 0.05)
        self.check_crit_chance_equal(self.mob_monster, 0.0)

        self.check_quest_markers([QUEST_OPTION_MARKERS.DISHONORABLE], habit_class=habits.Honor)
        self.check_quest_markers_reward_bonus([QUEST_OPTION_MARKERS.DISHONORABLE], habit_class=habits.Honor)

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.HONOR_EVENTS, set()), set([ACTION_EVENT.DISHONORABLE]))


    @mock.patch('the_tale.game.heroes.habits.Honor.interval', game_relations.HABIT_HONOR_INTERVAL.LEFT_2)
    def test_left_2(self):
        self.assertFalse(self.hero.check_attribute(MODIFIERS.KILL_BEFORE_BATTLE))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PICKED_UP_IN_ROAD))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_ENEMY, 1.0), 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_FRIEND, 1.0), 1.0)

        self.check_crit_chance_equal(self.mob_neutral, 0.0)
        self.check_crit_chance_equal(self.mob_civilized, 0.05)
        self.check_crit_chance_equal(self.mob_monster, 0.0)

        self.check_quest_markers([QUEST_OPTION_MARKERS.DISHONORABLE], habit_class=habits.Honor)
        self.check_quest_markers_reward_bonus([QUEST_OPTION_MARKERS.DISHONORABLE], habit_class=habits.Honor)

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.HONOR_EVENTS, set()), set([ACTION_EVENT.DISHONORABLE]))


    @mock.patch('the_tale.game.heroes.habits.Honor.interval', game_relations.HABIT_HONOR_INTERVAL.LEFT_1)
    def test_left_1(self):
        self.assertFalse(self.hero.check_attribute(MODIFIERS.KILL_BEFORE_BATTLE))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PICKED_UP_IN_ROAD))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_ENEMY, 1.0), 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_FRIEND, 1.0), 1.0)

        self.check_crit_chance_equal(self.mob_neutral, 0.0)
        self.check_crit_chance_equal(self.mob_civilized, 0.0)
        self.check_crit_chance_equal(self.mob_monster, 0.0)

        self.check_quest_markers([QUEST_OPTION_MARKERS.DISHONORABLE], habit_class=habits.Honor)
        self.check_quest_markers_reward_bonus([QUEST_OPTION_MARKERS.DISHONORABLE], habit_class=habits.Honor)

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.HONOR_EVENTS, set()), set([]))

    @mock.patch('the_tale.game.heroes.habits.Honor.interval', game_relations.HABIT_HONOR_INTERVAL.NEUTRAL)
    def test_neutral(self):
        self.assertFalse(self.hero.check_attribute(MODIFIERS.KILL_BEFORE_BATTLE))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PICKED_UP_IN_ROAD))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_ENEMY, 1.0), 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_FRIEND, 1.0), 1.0)

        self.check_crit_chance_equal(self.mob_neutral, 0.0)
        self.check_crit_chance_equal(self.mob_civilized, 0.0)
        self.check_crit_chance_equal(self.mob_monster, 0.0)

        self.check_quest_markers([], habit_class=habits.Honor)
        self.check_quest_markers_reward_bonus([], habit_class=habits.Honor)

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.HONOR_EVENTS, set()), set([]))

    @mock.patch('the_tale.game.heroes.habits.Honor.interval', game_relations.HABIT_HONOR_INTERVAL.RIGHT_1)
    def test_right_1(self):
        self.assertFalse(self.hero.check_attribute(MODIFIERS.KILL_BEFORE_BATTLE))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PICKED_UP_IN_ROAD))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_ENEMY, 1.0), 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_FRIEND, 1.0), 1.0)

        self.check_crit_chance_equal(self.mob_neutral, 0.0)
        self.check_crit_chance_equal(self.mob_civilized, 0.0)
        self.check_crit_chance_equal(self.mob_monster, 0.0)

        self.check_quest_markers([QUEST_OPTION_MARKERS.HONORABLE], habit_class=habits.Honor)
        self.check_quest_markers_reward_bonus([QUEST_OPTION_MARKERS.HONORABLE], habit_class=habits.Honor)

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.HONOR_EVENTS, set()), set([]))

    @mock.patch('the_tale.game.heroes.habits.Honor.interval', game_relations.HABIT_HONOR_INTERVAL.RIGHT_2)
    def test_right_2(self):
        self.assertFalse(self.hero.check_attribute(MODIFIERS.KILL_BEFORE_BATTLE))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PICKED_UP_IN_ROAD))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_ENEMY, 1.0), 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_FRIEND, 1.0), 1.0)

        self.check_crit_chance_equal(self.mob_neutral, 0.0)
        self.check_crit_chance_equal(self.mob_civilized, 0.0)
        self.check_crit_chance_equal(self.mob_monster, 0.04)

        self.check_quest_markers([QUEST_OPTION_MARKERS.HONORABLE], habit_class=habits.Honor)
        self.check_quest_markers_reward_bonus([QUEST_OPTION_MARKERS.HONORABLE], habit_class=habits.Honor)

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.HONOR_EVENTS, set()), set([ACTION_EVENT.NOBLE]))

    @mock.patch('the_tale.game.heroes.habits.Honor.interval', game_relations.HABIT_HONOR_INTERVAL.RIGHT_3)
    def test_right_3(self):
        self.assertFalse(self.hero.check_attribute(MODIFIERS.KILL_BEFORE_BATTLE))
        self.assertTrue(self.hero.check_attribute(MODIFIERS.PICKED_UP_IN_ROAD))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_ENEMY, 1.0), 1.0)
        self.assertTrue(self.hero.modify_attribute(MODIFIERS.POWER_TO_FRIEND, 1.0))

        self.check_crit_chance_equal(self.mob_neutral, 0.0)
        self.check_crit_chance_equal(self.mob_civilized, 0.0)
        self.check_crit_chance_equal(self.mob_monster, 0.04)

        self.check_quest_markers([QUEST_OPTION_MARKERS.HONORABLE], habit_class=habits.Honor)
        self.check_quest_markers_reward_bonus([QUEST_OPTION_MARKERS.HONORABLE], habit_class=habits.Honor)

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.HONOR_EVENTS, set()), set([ACTION_EVENT.NOBLE]))


@mock.patch('the_tale.game.balance.constants.EXP_FOR_KILL_PROBABILITY', 1.01)
@mock.patch('the_tale.game.balance.constants.PEACEFULL_BATTLE_PROBABILITY', 1.01)
class PeacefulnessHabitModifiersTest(BaseHabitTest):

    def setUp(self):
        super(PeacefulnessHabitModifiersTest, self).setUp()

        self.actor_hero = FakeActor(name='attacker')

        self.mob_neutral = FakeActor(name='defender', mob_type=game_relations.BEING_TYPE.PLANT)

        self.mob_civilized = FakeActor(name='defender', mob_type=game_relations.BEING_TYPE.CIVILIZED)
        self.mob_monster = FakeActor(name='defender', mob_type=game_relations.BEING_TYPE.MONSTER)


    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', game_relations.HABIT_PEACEFULNESS_INTERVAL.LEFT_3)
    def test_left_3(self):

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.FRIEND_QUEST_PRIORITY, 1.0), 1.0)
        self.assertTrue(self.hero.modify_attribute(MODIFIERS.ENEMY_QUEST_PRIORITY, 1.0) > 1.0)

        self.assertTrue(self.hero.check_attribute(MODIFIERS.EXP_FOR_KILL))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PEACEFULL_BATTLE))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.LOOT_PROBABILITY, 1.0), 1.0)

        self.check_first_strike(self.mob_neutral, True)
        self.check_first_strike(self.actor_hero, False)


        self.check_quest_markers([QUEST_OPTION_MARKERS.AGGRESSIVE], habit_class=habits.Peacefulness)
        self.check_quest_markers_reward_bonus([QUEST_OPTION_MARKERS.AGGRESSIVE], habit_class=habits.Peacefulness)

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.HONOR_EVENTS, set()), set([ACTION_EVENT.AGGRESSIVE]))


    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', game_relations.HABIT_PEACEFULNESS_INTERVAL.LEFT_2)
    def test_left_2(self):

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.FRIEND_QUEST_PRIORITY, 1.0), 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.ENEMY_QUEST_PRIORITY, 1.0), 1.0)

        self.assertFalse(self.hero.check_attribute(MODIFIERS.EXP_FOR_KILL))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PEACEFULL_BATTLE))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.LOOT_PROBABILITY, 1.0), 1.0)
        self.check_first_strike(self.mob_neutral, True)
        self.check_first_strike(self.actor_hero, False)

        self.check_quest_markers([QUEST_OPTION_MARKERS.AGGRESSIVE], habit_class=habits.Peacefulness)
        self.check_quest_markers_reward_bonus([QUEST_OPTION_MARKERS.AGGRESSIVE], habit_class=habits.Peacefulness)

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.HONOR_EVENTS, set()), set([ACTION_EVENT.AGGRESSIVE]))


    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', game_relations.HABIT_PEACEFULNESS_INTERVAL.LEFT_1)
    def test_left_1(self):
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.FRIEND_QUEST_PRIORITY, 1.0), 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.ENEMY_QUEST_PRIORITY, 1.0), 1.0)

        self.assertFalse(self.hero.check_attribute(MODIFIERS.EXP_FOR_KILL))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PEACEFULL_BATTLE))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.LOOT_PROBABILITY, 1.0), 1.0)
        self.check_first_strike(self.mob_neutral, False)
        self.check_first_strike(self.actor_hero, False)

        self.check_quest_markers([QUEST_OPTION_MARKERS.AGGRESSIVE], habit_class=habits.Peacefulness)
        self.check_quest_markers_reward_bonus([QUEST_OPTION_MARKERS.AGGRESSIVE], habit_class=habits.Peacefulness)

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.HONOR_EVENTS, set()), set([]))

    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', game_relations.HABIT_PEACEFULNESS_INTERVAL.NEUTRAL)
    def test_neutral(self):
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.FRIEND_QUEST_PRIORITY, 1.0), 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.ENEMY_QUEST_PRIORITY, 1.0), 1.0)

        self.assertFalse(self.hero.check_attribute(MODIFIERS.EXP_FOR_KILL))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PEACEFULL_BATTLE))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.LOOT_PROBABILITY, 1.0), 1.0)
        self.check_first_strike(self.mob_neutral, False)
        self.check_first_strike(self.actor_hero, False)

        self.check_quest_markers([], habit_class=habits.Peacefulness)
        self.check_quest_markers_reward_bonus([], habit_class=habits.Peacefulness)

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.HONOR_EVENTS, set()), set([]))

    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', game_relations.HABIT_PEACEFULNESS_INTERVAL.RIGHT_1)
    def test_right_1(self):
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.FRIEND_QUEST_PRIORITY, 1.0), 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.ENEMY_QUEST_PRIORITY, 1.0), 1.0)

        self.assertFalse(self.hero.check_attribute(MODIFIERS.EXP_FOR_KILL))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PEACEFULL_BATTLE))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.LOOT_PROBABILITY, 1.0), 1.0)
        self.check_first_strike(self.mob_neutral, False)
        self.check_first_strike(self.actor_hero, False)

        self.check_quest_markers([QUEST_OPTION_MARKERS.UNAGGRESSIVE], habit_class=habits.Peacefulness)
        self.check_quest_markers_reward_bonus([QUEST_OPTION_MARKERS.UNAGGRESSIVE], habit_class=habits.Peacefulness)

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.HONOR_EVENTS, set()), set([]))

    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', game_relations.HABIT_PEACEFULNESS_INTERVAL.RIGHT_2)
    def test_right_2(self):
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.FRIEND_QUEST_PRIORITY, 1.0), 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.ENEMY_QUEST_PRIORITY, 1.0), 1.0)

        self.assertFalse(self.hero.check_attribute(MODIFIERS.EXP_FOR_KILL))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PEACEFULL_BATTLE))

        self.assertTrue(self.hero.modify_attribute(MODIFIERS.LOOT_PROBABILITY, 1.0) > 1.0)
        self.check_first_strike(self.mob_neutral, False)
        self.check_first_strike(self.actor_hero, False)

        self.check_quest_markers([QUEST_OPTION_MARKERS.UNAGGRESSIVE], habit_class=habits.Peacefulness)
        self.check_quest_markers_reward_bonus([QUEST_OPTION_MARKERS.UNAGGRESSIVE], habit_class=habits.Peacefulness)

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.HONOR_EVENTS, set()), set([ACTION_EVENT.PEACEABLE]))

    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', game_relations.HABIT_PEACEFULNESS_INTERVAL.RIGHT_3)
    def test_right_3(self):
        self.assertTrue(self.hero.modify_attribute(MODIFIERS.FRIEND_QUEST_PRIORITY, 1.0) > 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.ENEMY_QUEST_PRIORITY, 1.0), 1.0)

        self.assertFalse(self.hero.check_attribute(MODIFIERS.EXP_FOR_KILL))
        self.assertTrue(self.hero.check_attribute(MODIFIERS.PEACEFULL_BATTLE))

        self.assertTrue(self.hero.modify_attribute(MODIFIERS.LOOT_PROBABILITY, 1.0) > 1.0)
        self.check_first_strike(self.mob_neutral, False)
        self.check_first_strike(self.actor_hero, False)

        self.check_quest_markers([QUEST_OPTION_MARKERS.UNAGGRESSIVE], habit_class=habits.Peacefulness)
        self.check_quest_markers_reward_bonus([QUEST_OPTION_MARKERS.UNAGGRESSIVE], habit_class=habits.Peacefulness)

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.HONOR_EVENTS, set()), set([ACTION_EVENT.PEACEABLE]))
