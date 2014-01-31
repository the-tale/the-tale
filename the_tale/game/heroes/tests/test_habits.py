# coding: utf-8

import contextlib

import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.actions.fake import FakeActor

from the_tale.game.mobs.relations import MOB_TYPE

from the_tale.game.balance import constants as c
from the_tale.game.logic import create_test_map
from the_tale.game.relations import GENDER
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.heroes.relations import HABIT_HONOR_INTERVAL, MODIFIERS


class BaseHabitTest(testcase.TestCase):

    def setUp(self):
        super(BaseHabitTest, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]


class HabitTest(BaseHabitTest):

    def test_raw_value(self):
        self.assertEqual(self.hero.habit_honor.raw_value, 0)

        self.hero._model.habit_honor = 500
        self.assertEqual(self.hero.habit_honor.raw_value, 500)

    def test_verbose_value(self):
        values = set()

        self.hero.habit_honor.change(-500)

        for gender in GENDER.records:
            self.hero.gender = gender
            values.add(self.hero.habit_honor.verbose_value)

        self.assertEqual(len(values), 3)

        self.hero.habit_honor.change(600)

        for gender in GENDER.records:
            self.hero.gender = gender
            values.add(self.hero.habit_honor.verbose_value)

        self.assertEqual(len(values), 6)


    def test_interval_and_change(self):
        self.assertTrue(self.hero.habit_honor.interval.is_NEUTRAL)
        for expected_interval, right_border in zip(self.hero.habit_honor.intervals.records, c.HABITS_RIGHT_BORDERS):
            self.hero.habit_honor.change(right_border - self.hero._model.habit_honor - 0.01)
            self.assertEqual(self.hero.habit_honor.interval, expected_interval)


class UpdateHabitsTest(BaseHabitTest):

    def setUp(self):
        super(UpdateHabitsTest, self).setUp()

        self.hero.habit_honor.change(500)
        self.hero.habit_aggressiveness.change(-500)


    @contextlib.contextmanager
    def check_habits_changed(self, d_honor, d_aggressiveness):
        with self.check_delta(lambda: self.hero.habit_honor.raw_value, d_honor):
            with self.check_delta(lambda: self.hero.habit_aggressiveness.raw_value, d_aggressiveness):
                yield


    def test_correlation_requirements__none(self):
        with self.check_habits_changed(-1, 1):
            self.hero.update_habits(mock.Mock(correlation_requirements=None, honor=-1, aggressiveness=1))

        with self.check_habits_changed(2, -2):
            self.hero.update_habits(mock.Mock(correlation_requirements=None, honor=2, aggressiveness=-2))


    def test_correlation_requirements__true(self):
        with self.check_habits_changed(0, 0):
            self.hero.update_habits(mock.Mock(correlation_requirements=True, honor=-1, aggressiveness=1))

        with self.check_habits_changed(2, -2):
            self.hero.update_habits(mock.Mock(correlation_requirements=True, honor=2, aggressiveness=-2))


    def test_correlation_requirements__false(self):
        with self.check_habits_changed(-1, 1):
            self.hero.update_habits(mock.Mock(correlation_requirements=False, honor=-1, aggressiveness=1))

        with self.check_habits_changed(0, 0):
            self.hero.update_habits(mock.Mock(correlation_requirements=False, honor=2, aggressiveness=-2))


@mock.patch('the_tale.game.balance.constants.KILL_BEFORE_BATTLE_PROBABILITY', 1.01)
@mock.patch('the_tale.game.balance.constants.PICKED_UP_IN_ROAD_PROBABILITY', 1.01)
@mock.patch('the_tale.game.mobs.storage.mobs_storage.mob_type_fraction', lambda mob_type: {MOB_TYPE.PLANT: 0.1,
                                                                                           MOB_TYPE.CIVILIZED: 0.3,
                                                                                           MOB_TYPE.MONSTER: 0.6}.get(mob_type, 0))
class HonorHabitModifiersTest(BaseHabitTest):

    def setUp(self):
        super(HonorHabitModifiersTest, self).setUp()

        self.actor_hero = FakeActor(name='attacker')

        self.mob_neutral = FakeActor(name='defender', mob_type=MOB_TYPE.PLANT)

        self.mob_civilized = FakeActor(name='defender', mob_type=MOB_TYPE.CIVILIZED)
        self.mob_monster = FakeActor(name='defender', mob_type=MOB_TYPE.MONSTER)

    def check_crit_chance_equal(self, mob, expected_crit_chance):
        self.actor_hero.context._on_every_turn()
        self.hero.update_context(self.actor_hero, mob)
        self.assertEqual(self.actor_hero.context.crit_chance, expected_crit_chance)

    @mock.patch('the_tale.game.heroes.habits.Honor.interval', HABIT_HONOR_INTERVAL.LEFT_3)
    def test_left_3(self):
        self.assertTrue(self.hero.check_attribute(MODIFIERS.KILL_BEFORE_BATTLE))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PICKED_UP_IN_ROAD))

        self.assertTrue(self.hero.modify_attribute(MODIFIERS.POWER_TO_ENEMY, 1.0) > 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_FRIEND, 1.0), 1.0)

        self.check_crit_chance_equal(self.mob_neutral, 0.0)
        self.check_crit_chance_equal(self.mob_civilized, 0.03)
        self.check_crit_chance_equal(self.mob_monster, 0.0)


    @mock.patch('the_tale.game.heroes.habits.Honor.interval', HABIT_HONOR_INTERVAL.LEFT_2)
    def test_left_2(self):
        self.assertFalse(self.hero.check_attribute(MODIFIERS.KILL_BEFORE_BATTLE))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PICKED_UP_IN_ROAD))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_ENEMY, 1.0), 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_FRIEND, 1.0), 1.0)

        self.check_crit_chance_equal(self.mob_neutral, 0.0)
        self.check_crit_chance_equal(self.mob_civilized, 0.03)
        self.check_crit_chance_equal(self.mob_monster, 0.0)


    @mock.patch('the_tale.game.heroes.habits.Honor.interval', HABIT_HONOR_INTERVAL.LEFT_1)
    def test_left_1(self):
        self.assertFalse(self.hero.check_attribute(MODIFIERS.KILL_BEFORE_BATTLE))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PICKED_UP_IN_ROAD))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_ENEMY, 1.0), 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_FRIEND, 1.0), 1.0)

        self.check_crit_chance_equal(self.mob_neutral, 0.0)
        self.check_crit_chance_equal(self.mob_civilized, 0.0)
        self.check_crit_chance_equal(self.mob_monster, 0.0)

    @mock.patch('the_tale.game.heroes.habits.Honor.interval', HABIT_HONOR_INTERVAL.NEUTRAL)
    def test_neutral(self):
        self.assertFalse(self.hero.check_attribute(MODIFIERS.KILL_BEFORE_BATTLE))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PICKED_UP_IN_ROAD))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_ENEMY, 1.0), 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_FRIEND, 1.0), 1.0)

        self.check_crit_chance_equal(self.mob_neutral, 0.0)
        self.check_crit_chance_equal(self.mob_civilized, 0.0)
        self.check_crit_chance_equal(self.mob_monster, 0.0)

    @mock.patch('the_tale.game.heroes.habits.Honor.interval', HABIT_HONOR_INTERVAL.RIGHT_1)
    def test_right_1(self):
        self.assertFalse(self.hero.check_attribute(MODIFIERS.KILL_BEFORE_BATTLE))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PICKED_UP_IN_ROAD))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_ENEMY, 1.0), 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_FRIEND, 1.0), 1.0)

        self.check_crit_chance_equal(self.mob_neutral, 0.0)
        self.check_crit_chance_equal(self.mob_civilized, 0.0)
        self.check_crit_chance_equal(self.mob_monster, 0.0)

    @mock.patch('the_tale.game.heroes.habits.Honor.interval', HABIT_HONOR_INTERVAL.RIGHT_2)
    def test_right_2(self):
        self.assertFalse(self.hero.check_attribute(MODIFIERS.KILL_BEFORE_BATTLE))
        self.assertFalse(self.hero.check_attribute(MODIFIERS.PICKED_UP_IN_ROAD))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_ENEMY, 1.0), 1.0)
        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_FRIEND, 1.0), 1.0)

        self.check_crit_chance_equal(self.mob_neutral, 0.0)
        self.check_crit_chance_equal(self.mob_civilized, 0.0)
        self.check_crit_chance_equal(self.mob_monster, 0.06)

    @mock.patch('the_tale.game.heroes.habits.Honor.interval', HABIT_HONOR_INTERVAL.RIGHT_3)
    def test_right_3(self):
        self.assertFalse(self.hero.check_attribute(MODIFIERS.KILL_BEFORE_BATTLE))
        self.assertTrue(self.hero.check_attribute(MODIFIERS.PICKED_UP_IN_ROAD))

        self.assertEqual(self.hero.modify_attribute(MODIFIERS.POWER_TO_ENEMY, 1.0), 1.0)
        self.assertTrue(self.hero.modify_attribute(MODIFIERS.POWER_TO_FRIEND, 1.0))

        self.check_crit_chance_equal(self.mob_neutral, 0.0)
        self.check_crit_chance_equal(self.mob_civilized, 0.0)
        self.check_crit_chance_equal(self.mob_monster, 0.06)
