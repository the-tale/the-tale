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
        self.assertEqual(c.TURN_DELTA, 10)
        self.assertEqual(c.TURNS_IN_HOUR, 360.0)
        self.assertEqual(c.POWER_PER_LVL, 1)
        self.assertEqual(c.EQUIP_SLOTS_NUMBER, 11)
        self.assertEqual(c.ARTIFACTS_PER_LVL, 4)

        self.assertEqual(c.EXP_PENALTY_MULTIPLIER, 0.1)
        self.assertEqual(c.EXP_PER_HOUR, 10)
        self.assertEqual(c.EXP_PER_QUEST_FRACTION, 0.33)
        self.assertEqual(c.EXP_FOR_PREMIUM_ACCOUNT, 1.0)
        self.assertEqual(c.EXP_FOR_NORMAL_ACCOUNT, 0.66)

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

        self.assertEqual(c.ANGEL_ENERGY_MAX, 12)
        self.assertEqual(c.ANGEL_ENERGY_PREMIUM_BONUS, 6)
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
        self.assertEqual(c.GAME_SECONDS_IN_TURN, 120)

        self.assertEqual(c.MAP_CELL_LENGTH, 3.0)
        self.assertEqual(c.MAP_SYNC_TIME_HOURS, 1)
        self.assertEqual(c.MAP_SYNC_TIME, 360)


        self.assertEqual(c.QUESTS_SPECIAL_FRACTION, 0.2)
        self.assertEqual(c.QUESTS_SHORT_PATH_LEVEL_CAP, 4)

        self.assertEqual(c.QUESTS_LOCK_TIME, { 'hunt': int(1.5*12*360),
                                               'hometown': int(12*360),
                                               'helpfriend': int(12*360),
                                               'interfereenemy': int(12*360),
                                               'searchsmith': int(0.5*12*360) })

        self.assertEqual(c.HERO_POWER_PER_DAY, 1000)
        self.assertEqual(c.PERSON_POWER_PER_QUEST_FRACTION, 0.33)
        self.assertEqual(c.PERSON_POWER_FOR_RANDOM_SPEND, 200)

        self.assertEqual(c.CHARACTER_PREFERENCES_CHANGE_DELAY, 60*60*24*7)

        self.assertEqual(c.ABILITIES_ACTIVE_MAXIMUM, 5)
        self.assertEqual(c.ABILITIES_PASSIVE_MAXIMUM, 2)

        self.assertEqual(c.ABILITIES_BATTLE_MAXIMUM, 7)
        self.assertEqual(c.ABILITIES_NONBATTLE_MAXUMUM, 4)
        self.assertEqual(c.ABILITIES_OLD_ABILITIES_FOR_CHOOSE_MAXIMUM, 2)
        self.assertEqual(c.ABILITIES_FOR_CHOOSE_MAXIMUM, 4)

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
        self.assertEqual(c.PLACE_TRANSPORT_FROM_BEST_PERSON, 0.2)
        self.assertEqual(c.PLACE_FREEDOM_FROM_BEST_PERSON, 0.2)

        self.assertEqual(c.PLACE_MAX_EXCHANGED_NUMBER, 3)

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
