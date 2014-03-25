# coding: utf-8

from the_tale.common.utils import testcase


from . import formulas as f, constants as c, enums as e

E = 0.00001

class ConstantsTest(testcase.TestCase):

    def test_constants_values(self): # pylint: disable=R0915

        self.assertEqual(c.TIME_TO_LVL_DELTA, 5.0)
        self.assertEqual(c.INITIAL_HP, 500)
        self.assertEqual(c.HP_PER_LVL, 50)
        self.assertEqual(c.MOB_HP_MULTIPLIER, 0.25)
        self.assertEqual(c.BOSS_HP_MULTIPLIER, 0.5)
        self.assertEqual(c.TURN_DELTA, 10)
        self.assertEqual(c.TURNS_IN_HOUR, 360.0)
        self.assertEqual(c.POWER_PER_LVL, 1)
        self.assertEqual(c.EQUIP_SLOTS_NUMBER, 11)
        self.assertEqual(c.ARTIFACTS_PER_LVL, 4)

        self.assertEqual(c.EXP_PER_HOUR, 10)
        self.assertEqual(c.EXP_PER_QUEST_FRACTION, 0.33)
        self.assertEqual(c.EXP_FOR_PREMIUM_ACCOUNT, 0.8)
        self.assertEqual(c.EXP_FOR_NORMAL_ACCOUNT, 0.528)

        self.assertEqual(c.HERO_MOVE_SPEED, 0.3)
        self.assertEqual(c.BATTLE_LENGTH, 16)
        self.assertEqual(c.INTERVAL_BETWEEN_BATTLES, 3)
        self.assertEqual(c.BATTLES_BEFORE_HEAL, 8)
        self.assertEqual(c.HEAL_TIME_FRACTION, 0.2)
        self.assertEqual(c.HEAL_STEP_FRACTION, 0.2)

        self.assertEqual(c.HEALTH_IN_SETTLEMENT_TO_START_HEAL_FRACTION, 0.33)
        self.assertEqual(c.HEALTH_IN_MOVE_TO_START_HEAL_FRACTION, 0.25)

        self.assertEqual(c.TURNS_TO_IDLE, 6)
        self.assertEqual(c.TURNS_TO_RESURRECT, 18)

        self.assertEqual(c.GET_LOOT_PROBABILITY, 0.33)
        self.assertEqual(c.NORMAL_LOOT_PROBABILITY, 0.99)
        self.assertEqual(c.RARE_LOOT_PROBABILITY, 0.0099)
        self.assertTrue(c.EPIC_LOOT_PROBABILITY - 0.0001 < 1e-10)
        self.assertEqual(c.NORMAL_LOOT_COST, 1.5)
        self.assertEqual(c.RARE_LOOT_COST, 25.0)
        self.assertEqual(c.EPIC_LOOT_COST, 250.0)
        self.assertEqual(c.NORMAL_ACTION_PRICE_MULTIPLYER, 1.2)
        self.assertEqual(c.BASE_EXPERIENCE_FOR_MONEY_SPEND, 96)
        self.assertEqual(c.EXPERIENCE_DELTA_FOR_MONEY_SPEND, 0.5)

        self.assertEqual(c.SELL_ARTIFACT_PRICE_FRACTION, 0.15)
        self.assertEqual(c.PRICE_DELTA, 0.2)
        self.assertEqual(c.POWER_TO_LVL, 11.0)
        self.assertEqual(c.ARTIFACT_POWER_DELTA, 0.2)
        self.assertEqual(c.ARTIFACT_BETTER_MIN_POWER_DELTA, 5)
        self.assertEqual(c.BATTLES_LINE_LENGTH, 8*(16+3)-3)
        self.assertEqual(c.BATTLES_PER_TURN, 1.0 / (3+1) )
        self.assertEqual(c.HEAL_LENGTH, int((8*(16+3)-3) * 0.2))
        self.assertEqual(c.ACTIONS_CYCLE_LENGTH, int(8*(16+3)-3 + (8*(16+3)-3) * 0.2))
        self.assertEqual(c.BATTLES_PER_HOUR, 360.0 / (int(8*(16+3)-3 + (8*(16+3)-3) * 0.2)) * 8)
        self.assertEqual(c.DAMAGE_TO_HERO_PER_HIT_FRACTION, 1.0 / (8*16/2))
        self.assertEqual(c.DAMAGE_TO_MOB_PER_HIT_FRACTION, 1.0 / (16/2))
        self.assertEqual(c.DAMAGE_DELTA, 0.2)
        self.assertEqual(c.DAMAGE_CRIT_MULTIPLIER, 2.0)

        self.assertEqual(c.MAX_BAG_SIZE, 12)
        self.assertEqual(c.BAG_SIZE_TO_SELL_LOOT_FRACTION, 0.33)

        self.assertEqual(c.DESTINY_POINT_IN_LEVELS, 5)
        self.assertEqual(c.SPEND_MONEY_FOR_HEAL_HEALTH_FRACTION, 0.75)

        self.assertEqual(c.ANGEL_ENERGY_MAX, 12)
        self.assertEqual(c.ANGEL_ENERGY_PREMIUM_BONUS, 6)
        self.assertEqual(c.ANGEL_FREE_ENERGY_MAXIMUM, 50)
        self.assertEqual(c.ANGEL_FREE_ENERGY_CHARGE, 10)
        self.assertEqual(c.ANGEL_FREE_ENERGY_CHARGE_CRIT, 20)
        self.assertEqual(c.ANGEL_ENERGY_REGENERATION_TIME,  0.5)
        self.assertEqual(c.ANGEL_ENERGY_REGENERATION_PERIOD,  180)
        self.assertEqual(c.ANGEL_ENERGY_REGENERATION_AMAUNT, 1)

        self.assertEqual(c.ANGEL_ENERGY_REGENERATION_DELAY, { e.ANGEL_ENERGY_REGENERATION_TYPES.PRAY: 1,
                                                              e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE: 2,
                                                              e.ANGEL_ENERGY_REGENERATION_TYPES.INCENSE: 4,
                                                              e.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS: 3,
                                                              e.ANGEL_ENERGY_REGENERATION_TYPES.MEDITATION: 2 })

        self.assertEqual(c.ANGEL_ENERGY_REGENERATION_STEPS, { e.ANGEL_ENERGY_REGENERATION_TYPES.PRAY: 3,
                                                              e.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE: 5,
                                                              e.ANGEL_ENERGY_REGENERATION_TYPES.INCENSE: 6,
                                                              e.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS: 4,
                                                              e.ANGEL_ENERGY_REGENERATION_TYPES.MEDITATION: 4 })

        self.assertEqual(c.ANGEL_HELP_COST, 4)
        self.assertEqual(c.ANGEL_ARENA_COST, 1)
        self.assertEqual(c.ANGEL_HELP_HEAL_IF_LOWER_THEN, float(0.8))

        self.assertEqual(c.ANGEL_HELP_HEAL_FRACTION,  (float(0.25), float(0.5)))
        self.assertEqual(c.ANGEL_HELP_TELEPORT_DISTANCE, float(3.0))
        self.assertEqual(c.ANGEL_HELP_LIGHTING_FRACTION, (float(0.25), float(0.5)))
        self.assertEqual(c.ANGEL_HELP_EXPERIENCE, 20)

        self.assertEqual(c.ANGEL_HELP_EXPERIENCE_DELTA, 0.5)

        self.assertEqual(c.ANGEL_HELP_CRIT_HEAL_FRACTION,  (float(0.5), float(0.75)))
        self.assertEqual(c.ANGEL_HELP_CRIT_TELEPORT_DISTANCE, float(9.0))
        self.assertEqual(c.ANGEL_HELP_CRIT_LIGHTING_FRACTION, (float(0.5), float(0.75)))
        self.assertEqual(c.ANGEL_HELP_CRIT_MONEY_MULTIPLIER, int(10))
        self.assertEqual(c.ANGEL_HELP_CRIT_EXPERIENCE, 60)

        self.assertEqual(c.ANGEL_ENERGY_INSTANT_REGENERATION_IN_PLACE, 4)


        self.assertEqual(c.GAME_SECONDS_IN_GAME_MINUTE, 60)
        self.assertEqual(c.GAME_MINUTES_IN_GAME_HOUR, 60)
        self.assertEqual(c.GAME_HOURSE_IN_GAME_DAY, 24)
        self.assertEqual(c.GAME_DAYS_IN_GAME_WEEK, 7)
        self.assertEqual(c.GAME_WEEKS_IN_GAME_MONTH, 4)
        self.assertEqual(c.GAME_MONTH_IN_GAME_YEAR, 4)

        self.assertEqual(c.GAME_SECONDS_IN_GAME_HOUR, 60*60)
        self.assertEqual(c.GAME_SECONDS_IN_GAME_DAY, 60*60*24)
        self.assertEqual(c.GAME_SECONDS_IN_GAME_WEEK, 60*60*24*7)
        self.assertEqual(c.GAME_SECONDS_IN_GAME_MONTH, 60*60*24*7*4)
        self.assertEqual(c.GAME_SECONDS_IN_GAME_YEAR, 60*60*24*7*4*4)

        self.assertEqual(c.TURNS_IN_GAME_MONTH, 20160)
        self.assertEqual(c.TURNS_IN_GAME_YEAR, 20160 * 4)
        self.assertEqual(c.GAME_SECONDS_IN_TURN, 120)

        self.assertEqual(c.MAP_CELL_LENGTH, 3.0)
        self.assertEqual(c.MAP_SYNC_TIME_HOURS, 1)
        self.assertEqual(c.MAP_SYNC_TIME, 360)


        self.assertEqual(c.QUESTS_SHORT_PATH_LEVEL_CAP, 4)
        self.assertEqual(c.QUESTS_PILGRIMAGE_FRACTION, 0.025)

        self.assertEqual(c.HERO_POWER_PER_DAY, 1000)
        self.assertEqual(c.PERSON_POWER_PER_QUEST_FRACTION, 0.33)
        self.assertEqual(c.PERSON_POWER_FOR_RANDOM_SPEND, 200)
        self.assertEqual(c.HERO_POWER_BONUS, 0.01)

        self.assertEqual(c.CHARACTER_PREFERENCES_CHANGE_DELAY, 60*60*24*7)
        self.assertEqual(c.POSITIVE_NEGATIVE_POWER_RELATION, 2.0)

        self.assertEqual(c.ABILITIES_ACTIVE_MAXIMUM, 5)
        self.assertEqual(c.ABILITIES_PASSIVE_MAXIMUM, 2)

        self.assertEqual(c.ABILITIES_BATTLE_MAXIMUM, 7)
        self.assertEqual(c.ABILITIES_NONBATTLE_MAXUMUM, 4)
        self.assertEqual(c.ABILITIES_OLD_ABILITIES_FOR_CHOOSE_MAXIMUM, 2)
        self.assertEqual(c.ABILITIES_FOR_CHOOSE_MAXIMUM, 4)

        self.assertEqual(c.HABITS_BORDER, 1000)
        self.assertEqual(c.HABITS_RIGHT_BORDERS, [-700, -300, -100, 100, 300, 700, 1001])
        self.assertEqual(c.HABITS_QUEST_ACTIVE_DELTA, 20.0)
        self.assertEqual(c.HABITS_QUEST_PASSIVE_DELTA, 0.6)
        self.assertEqual(round(c.HABITS_HELP_ABILITY_DELTA, 5), 2.77778)
        self.assertEqual(round(c.HABITS_ARENA_ABILITY_DELTA, 5), 0.69444)
        self.assertEqual(round(c.HABITS_PERIODIC_DELTA, 5), 2.0)

        self.assertEqual(c.HABITS_QUEST_ACTIVE_PREMIUM_MULTIPLIER, 1.5)

        self.assertEqual(c.KILL_BEFORE_BATTLE_PROBABILITY, 0.05)
        self.assertEqual(c.PICKED_UP_IN_ROAD_TELEPORT_LENGTH, 3.0)
        self.assertEqual(round(c.PICKED_UP_IN_ROAD_SPEED_BONUS, 5), 0.07018)
        self.assertEqual(round(c.PICKED_UP_IN_ROAD_PROBABILITY, 5), 0.02339)

        self.assertEqual(c.HABIT_QUEST_PRIORITY_MODIFIER, 2.0)

        self.assertEqual(c.HONOR_POWER_BONUS_FRACTION, 0.25)
        self.assertEqual(c.MONSTER_TYPE_BATTLE_CRIT_MAX_CHANCE, 0.02)

        self.assertEqual(c.HABIT_QUEST_REWARD_MAX_BONUS, 0.25)
        self.assertEqual(c.HABIT_LOOT_PROBABILITY_MODIFIER, 1.2)

        self.assertEqual(c.EXP_FOR_KILL, 20)
        self.assertEqual(c.EXP_FOR_KILL_DELTA, 0.3)
        self.assertEqual(round(c.EXP_FOR_KILL_PROBABILITY, 5), 0.0024)

        self.assertEqual(c.HABIT_EVENTS_IN_DAY, 1.33)
        self.assertEqual(round(c.HABIT_EVENTS_IN_TURN, 5), 0.00015)

        self.assertEqual(round(c.HABIT_MOVE_EVENTS_IN_TURN, 5), 0.00015)
        self.assertEqual(round(c.HABIT_IN_PLACE_EVENTS_IN_TURN, 5), 0.00154)

        self.assertEqual(c.HABIT_EVENT_NOTHING_PRIORITY, 4)
        self.assertEqual(c.HABIT_EVENT_MONEY_PRIORITY, 4)
        self.assertEqual(c.HABIT_EVENT_ARTIFACT_PRIORITY, 2)
        self.assertEqual(c.HABIT_EVENT_EXPERIENCE_PRIORITY, 1)

        self.assertEqual(c.HABIT_EVENT_EXPERIENCE, 99)
        self.assertEqual(c.HABIT_EVENT_EXPERIENCE_DELTA, 0.5)


        self.assertEqual(c.DAMAGE_PVP_ADVANTAGE_MODIFIER, 0.5)
        self.assertEqual(c.DAMAGE_PVP_FULL_ADVANTAGE_STRIKE_MODIFIER, 5)
        self.assertEqual(c.PVP_MAX_ADVANTAGE_STEP, 0.25)
        self.assertEqual(c.PVP_ADVANTAGE_BARIER, 0.95)
        self.assertEqual(c.PVP_EFFECTIVENESS_EXTINCTION_FRACTION, 0.1)
        self.assertEqual(c.PVP_EFFECTIVENESS_STEP, 10)
        self.assertEqual(c.PVP_EFFECTIVENESS_INITIAL, 300)

        self.assertEqual(c.PLACE_TYPE_NECESSARY_BORDER, 75)
        self.assertEqual(c.PLACE_TYPE_ENOUGH_BORDER, 50)

        self.assertEqual(c.PLACE_GOODS_BONUS, 100)
        self.assertEqual(c.PLACE_GOODS_TO_LEVEL, 6000)
        self.assertEqual(c.PLACE_GOODS_AFTER_LEVEL_UP, 0.25)
        self.assertEqual(c.PLACE_GOODS_AFTER_LEVEL_DOWN, 0.75)
        self.assertEqual(c.PLACE_SAFETY_FROM_BEST_PERSON, 0.05)
        self.assertEqual(round(c.PLACE_TRANSPORT_FROM_BEST_PERSON, 5), 0.33333)
        self.assertEqual(round(c.PLACE_FREEDOM_FROM_BEST_PERSON, 5), 0.33333)

        self.assertEqual(c.PLACE_MAX_EXCHANGED_NUMBER, 3)

        self.assertEqual(c.PLACE_RACE_CHANGE_DELTA_IN_DAY, 0.1)
        self.assertEqual(c.PLACE_RACE_CHANGE_DELTA, 0.1 / 24)
        self.assertEqual(c.PLACE_ADD_PERSON_DELAY, 8640)

        self.assertEqual(c.BUILDING_MASTERY_BONUS, 0.15)
        self.assertEqual(c.BUILDING_FULL_DESTRUCTION_TIME, 2*7*24)
        self.assertTrue(0.0029 < c.BUILDING_AMORTIZATION_SPEED < 0.0030)
        self.assertEqual(c.BUILDING_FULL_REPAIR_ENERGY_COST, 168.0)
        self.assertEqual(c.BUILDING_AMORTIZATION_MODIFIER, 1.5)
        self.assertEqual(c.BUILDING_WORKERS_ENERGY_COST, 3)
        self.assertEqual(c.BUILDING_PERSON_POWER_MULTIPLIER, 1.1)
        self.assertEqual(c.BUILDING_TERRAIN_POWER_MULTIPLIER, 0.5)


class FormulasTest(testcase.TestCase):

    LVLS = [1, 2, 3, 4, 5, 7, 11, 17, 19, 25, 30, 40, 60, 71, 82, 99, 101]

    def test_lvl_after_time(self):
        for lvl in self.LVLS:
            # print lvl, f.total_time_for_lvl(lvl), f.lvl_after_time(f.total_time_for_lvl(lvl))
            self.assertEqual(lvl, f.lvl_after_time(f.total_time_for_lvl(lvl)))


    def test_expected_lvl_from_power(self):
        for lvl in self.LVLS:
            self.assertEqual(lvl, f.expected_lvl_from_power(f.clean_power_to_lvl(lvl) + f.power_to_lvl(lvl)))

        self.assertTrue(f.expected_lvl_from_power(1) < 1)

        self.assertEqual(0, f.expected_lvl_from_power(0))

    def test_sell_artifact_price(self):

        self.assertTrue(f.sell_artifact_price(1))

    def test_turns_to_game_time(self):

        self.assertEqual(f.turns_to_game_time(0), (0, 1, 1, 0, 0, 0))
        self.assertEqual(f.turns_to_game_time(1), (0, 1, 1, 0, 2, 0))
        self.assertEqual(f.turns_to_game_time(5), (0, 1, 1, 0, 10, 0))
        self.assertEqual(f.turns_to_game_time(20), (0, 1, 1, 0, 40, 0))
        self.assertEqual(f.turns_to_game_time(70), (0, 1, 1, 2, 20, 0))
        self.assertEqual(f.turns_to_game_time(700), (0, 1, 1, 23, 20, 0))
        self.assertEqual(f.turns_to_game_time(7001), (0, 1, 10, 17, 22, 0))
        self.assertEqual(f.turns_to_game_time(70010), (0, 4, 14, 5, 40, 0))
        self.assertEqual(f.turns_to_game_time(700103), (8, 3, 21, 8, 46, 0))
        self.assertEqual(f.turns_to_game_time(7001038), (86, 4, 8, 15, 56, 0))

    def test_experience_for_quest(self):
        self.assertTrue(f.experience_for_quest(100) < f.experience_for_quest(1000)< f.experience_for_quest(10000))
        self.assertEqual(int(f.experience_for_quest__real(100)), 151)

    def test_person_power_for_quest(self):
        self.assertTrue(f.person_power_for_quest(100) < f.person_power_for_quest(1000)< f.person_power_for_quest(10000))
        self.assertEqual(int(f.person_power_for_quest__real(100)), 572)

    def test_better_artifact_power(self):
        median_power = f.power_to_artifact(100)
        for i in xrange(100):
            self.assertTrue(median_power < f.power_to_better_artifact_randomized(100))

    def test_better_artifact_power__on_low_levels(self):
        self.assertEqual(f.power_to_artifact(1), 1)

        self.assertEqual(1 + c.ARTIFACT_BETTER_MIN_POWER_DELTA*2,
                         len(set(f.power_to_better_artifact_randomized(1) for i in xrange(100))))



# if one of this tests broken, we MUST review appropriate achievements' barriers
class AchievementsBarriers(testcase.TestCase):

    def money_after_months(self, months):
        return f.total_gold_at_lvl(f.lvl_after_time(months*30*24))

    def check_money(self, months, money):
        # print months, self.money_after_months(months) , self.money_after_months(months+0.25)
        self.assertTrue(self.money_after_months(months) <= money <= self.money_after_months(months+0.25))

    def test_money(self):
        self.check_money(0.1, 1000)
        self.check_money(0.5, 10000)
        self.check_money(1.4, 50000)
        self.check_money(7, 500000)
        self.check_money(11.25, 1000000)
        self.check_money(33.5, 5000000)


    def mobs_after_months(self, months):
        return int(c.BATTLES_PER_HOUR * months * 30 * 24)

    def check_mobs(self, months, mobs):
        # print months, self.mobs_after_months(months) , self.mobs_after_months(months+0.05)
        self.assertTrue(self.mobs_after_months(months) <= mobs <= self.mobs_after_months(months+0.05))

    def test_mobs(self):
        self.check_mobs(0.08, 1000)
        self.check_mobs(0.4, 5000)
        self.check_mobs(1.25, 15000)
        self.check_mobs(4.25, 50000)
        self.check_mobs(8.6, 100500)
        self.check_mobs(12.85, 150000)
        self.check_mobs(21.45, 250000)
        self.check_mobs(34.3, 400000)


    def artifacts_after_months(self, months):
        MAGIC = 1.5 # magic cooficient, to spend money events and abilities
        return int(c.ARTIFACTS_PER_LVL * (f.lvl_after_time(months*30*24)-1) * MAGIC)

    def check_artifacts(self, months, artifacts):
        # print months, self.artifacts_after_months(months) , self.artifacts_after_months(months+0.25)
        self.assertTrue(self.artifacts_after_months(months) <= artifacts <= self.artifacts_after_months(months+0.25))

    def test_artifacts(self):
        self.check_artifacts(0, 1)
        self.check_artifacts(0.2, 50)
        self.check_artifacts(0.9, 100)
        self.check_artifacts(6.2, 250)
        self.check_artifacts(24.6, 500)
        self.check_artifacts(55, 750)
