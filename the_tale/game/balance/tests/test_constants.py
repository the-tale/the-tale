# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.balance import constants as c, enums as e

E = 0.00001


class ConstantsTest(testcase.TestCase):

    def test_constants_values(self): # pylint: disable=R0915

        self.assertEqual(c.TIME_TO_LVL_DELTA, 7.0)
        self.assertEqual(c.TIME_TO_LVL_MULTIPLIER, 1.02)
        self.assertEqual(c.INITIAL_HP, 500)
        self.assertEqual(c.HP_PER_LVL, 50)
        self.assertEqual(c.MOB_HP_MULTIPLIER, 0.25)
        self.assertEqual(c.BOSS_HP_MULTIPLIER, 0.5)
        self.assertEqual(c.TURN_DELTA, 10)
        self.assertEqual(c.TURNS_IN_HOUR, 360.0)
        self.assertEqual(c.POWER_PER_LVL, 1)
        self.assertEqual(c.EQUIP_SLOTS_NUMBER, 11)

        self.assertEqual(c.ARTIFACTS_LOOT_PER_DAY, 1.0)
        self.assertEqual(c.ARTIFACT_FOR_QUEST_PROBABILITY, 0.1)
        self.assertEqual(round(c.ARTIFACTS_BREAKING_SPEED, 2), 0.37)

        self.assertEqual(c.EQUIPMENT_BREAK_FRACTION, 0.5)
        self.assertEqual(c.NORMAL_SLOT_REPAIR_PRIORITY, 1.0)
        self.assertEqual(c.SPECIAL_SLOT_REPAIR_PRIORITY, 2.0)

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

        self.assertEqual(c.GET_LOOT_PROBABILITY, 0.50)
        self.assertEqual(c.NORMAL_ARTIFACT_PROBABILITY, 1 - 0.05 - 0.005)
        self.assertEqual(c.RARE_ARTIFACT_PROBABILITY, 0.05)
        self.assertTrue(c.EPIC_ARTIFACT_PROBABILITY, 0.005)
        self.assertEqual(c.NORMAL_LOOT_COST, 1.0)
        self.assertEqual(c.BASE_EXPERIENCE_FOR_MONEY_SPEND, 96)
        self.assertEqual(c.EXPERIENCE_DELTA_FOR_MONEY_SPEND, 0.5)

        self.assertEqual(c.SELL_ARTIFACT_PRICE_MULTIPLIER, 10)
        self.assertEqual(c.POWER_TO_LVL, 11.0)
        self.assertEqual(c.ARTIFACT_POWER_DELTA, 0.2)
        self.assertEqual(c.ARTIFACT_BETTER_MIN_POWER_DELTA, 5)
        self.assertEqual(c.ARTIFACT_INTEGRITY_DAMAGE_PER_BATTLE, 1)
        self.assertEqual(c.ARTIFACT_INTEGRITY_SAFE_PROBABILITY_FOR_FAVORITE_ITEM, 0.5)

        self.assertEqual(c.ARTIFACT_RARE_MAX_INTEGRITY_MULTIPLIER, 1.5)
        self.assertEqual(c.ARTIFACT_EPIC_MAX_INTEGRITY_MULTIPLIER, 2)
        self.assertEqual(c.ARTIFACT_MAX_INTEGRITY_DELTA, 0.25)

        self.assertEqual(c.ARTIFACT_MAX_INTEGRITY, 11000)
        self.assertEqual(c.ARTIFACT_SHARP_MAX_INTEGRITY_LOST_FRACTION, 0.02)
        self.assertEqual(c.ARTIFACT_INTEGRITY_SAFE_BARRIER, 0.2)
        self.assertEqual(c.ARTIFACT_BREAK_POWER_FRACTIONS, (0.2, 0.3))
        self.assertEqual(c.ARTIFACT_BREAK_INTEGRITY_FRACTIONS, (0.1, 0.2))
        self.assertEqual(c.BATTLES_LINE_LENGTH, 8*(16+3)-3)
        self.assertEqual(c.BATTLES_PER_TURN, 1.0 / (3+1) )
        self.assertEqual(c.MAX_BATTLES_PER_TURN, 0.9 )
        self.assertEqual(c.WHILD_BATTLES_PER_TURN_BONUS, 0.05)
        self.assertEqual(c.HEAL_LENGTH, int((8*(16+3)-3) * 0.2))

        self.assertEqual(c.ACTIONS_CYCLE_LENGTH, int((8*(16+3)-3 + (8*(16+3)-3) * 0.2) / 0.95))

        self.assertEqual(c.BATTLES_PER_HOUR, 15.319148936170212)

        self.assertEqual(c.ARTIFACTS_PER_BATTLE, 0.0027199074074074074)
        self.assertEqual(c.ARTIFACTS_BREAKS_PER_BATTLE, 0.0009972993827160493)
        self.assertEqual(c.ARTIFACT_FROM_PREFERED_SLOT_PROBABILITY, 0.25)

        self.assertEqual(c.DAMAGE_TO_HERO_PER_HIT_FRACTION, 0.019230769230769232)
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
        self.assertEqual(c.QUEST_AREA_RADIUS, 180)
        self.assertEqual(c.QUEST_AREA_SHORT_RADIUS, 90)
        self.assertEqual(c.QUEST_AREA_MAXIMUM_RADIUS, 3000000)

        self.assertEqual(c.MAP_SYNC_TIME_HOURS, 1)
        self.assertEqual(c.MAP_SYNC_TIME, 360)


        self.assertEqual(c.QUESTS_SHORT_PATH_LEVEL_CAP, 4)
        self.assertEqual(c.QUESTS_PILGRIMAGE_FRACTION, 0.025)
        self.assertEqual(c.QUESTS_SOCIAL_CONNECTIONS_FRACTION, 0.05)

        self.assertEqual(c.HERO_POWER_PER_DAY, 1000)
        self.assertEqual(c.PERSON_POWER_PER_QUEST_FRACTION, 0.33)
        self.assertEqual(c.PERSON_POWER_FOR_RANDOM_SPEND, 200)
        self.assertEqual(c.HERO_POWER_BONUS, 0.01)

        self.assertEqual(c.PREFERENCES_CHANGE_DELAY, 2*7*24*60*60)
        self.assertEqual(c.PREFERED_MOB_LOOT_PROBABILITY_MULTIPLIER, 2)

        self.assertEqual(c.POSITIVE_NEGATIVE_POWER_RELATION, 4.0)

        self.assertEqual(c.ABILITIES_ACTIVE_MAXIMUM, 5)
        self.assertEqual(c.ABILITIES_PASSIVE_MAXIMUM, 2)

        self.assertEqual(c.ABILITIES_BATTLE_MAXIMUM, 7)
        self.assertEqual(c.ABILITIES_NONBATTLE_MAXIMUM, 4)
        self.assertEqual(c.ABILITIES_COMPANION_MAXIMUM, 4)
        self.assertEqual(c.ABILITIES_OLD_ABILITIES_FOR_CHOOSE_MAXIMUM, 2)
        self.assertEqual(c.ABILITIES_FOR_CHOOSE_MAXIMUM, 4)

        self.assertEqual(c.HABITS_BORDER, 1000)
        self.assertEqual(c.HABITS_RIGHT_BORDERS, [-700, -300, -100, 100, 300, 700, 1001])
        self.assertEqual(c.HABITS_QUEST_ACTIVE_DELTA, 20.0)
        self.assertEqual(c.HABITS_QUEST_PASSIVE_DELTA, 1.0)
        self.assertEqual(round(c.HABITS_HELP_ABILITY_DELTA, 5), 1.38889)
        self.assertEqual(round(c.HABITS_ARENA_ABILITY_DELTA, 5), 0.34722)

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
        self.assertEqual(round(c.EXP_FOR_KILL_PROBABILITY, 5), 0.00256)

        self.assertEqual(c.COMPANIONS_BONUS_EXP_FRACTION, 0.2)

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
        self.assertEqual(c.PLACE_KEEPERS_GOODS_SPENDING, 0.05)

        self.assertEqual(c.PLACE_SAFETY_FROM_BEST_PERSON, 0.05)
        self.assertEqual(round(c.PLACE_TRANSPORT_FROM_BEST_PERSON, 5), 0.33333)
        self.assertEqual(round(c.PLACE_FREEDOM_FROM_BEST_PERSON, 5), 0.33333)

        self.assertEqual(c.PLACE_MAX_BILLS_NUMBER, 3)

        self.assertEqual(c.PLACE_RACE_CHANGE_DELTA_IN_DAY, 0.1)
        self.assertEqual(c.PLACE_RACE_CHANGE_DELTA, 0.1 / 24)
        self.assertEqual(c.PLACE_ADD_PERSON_DELAY, 8640)

        self.assertEqual(c.PLACE_STABILITY_PER_BILL, 0.1)
        self.assertEqual(round(c.PLACE_STABILITY_PER_HOUR, 4), 0.0006)

        self.assertEqual(c.PLACE_STABILITY_MAX_PRODUCTION_PENALTY, -200)
        self.assertEqual(c.PLACE_STABILITY_MAX_SAFETY_PENALTY, -0.25)
        self.assertEqual(round(c.PLACE_STABILITY_MAX_TRANSPORT_PENALTY, 2), -0.67)
        self.assertEqual(round(c.PLACE_STABILITY_MAX_FREEDOM_PENALTY, 2), 0.67)

        self.assertEqual(c.WHILD_TRANSPORT_PENALTY, 0.1)
        self.assertEqual(c.TRANSPORT_FROM_PLACE_SIZE_PENALTY, 0.05)

        self.assertEqual(c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM, 10)
        self.assertEqual(c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM_PENALTY, 10)
        self.assertEqual(c.PLACE_HABITS_EVENT_PROBABILITY, 0.025)

        self.assertEqual(c.BUILDING_MASTERY_BONUS, 0.15)
        self.assertEqual(c.BUILDING_FULL_DESTRUCTION_TIME, 2*7*24)
        self.assertTrue(0.0029 < c.BUILDING_AMORTIZATION_SPEED < 0.0030)
        self.assertEqual(c.BUILDING_FULL_REPAIR_ENERGY_COST, 168.0)
        self.assertEqual(c.BUILDING_AMORTIZATION_MODIFIER, 1.5)
        self.assertEqual(c.BUILDING_WORKERS_ENERGY_COST, 3)
        self.assertEqual(c.BUILDING_PERSON_POWER_MULTIPLIER, 1.1)
        self.assertEqual(c.BUILDING_TERRAIN_POWER_MULTIPLIER, 0.5)

        self.assertEqual(c.CARDS_HELP_COUNT_TO_NEW_CARD, 18)
        self.assertEqual(c.CARDS_COMBINE_TO_UP_RARITY, 3)

        self.assertEqual(c.COMPANIONS_DEFENDS_IN_BATTLE, 1.5)
        self.assertEqual(c.COMPANIONS_HEAL_FRACTION, 0.05)

        self.assertEqual(c.COMPANIONS_MIN_COHERENCE, 0)
        self.assertEqual(c.COMPANIONS_MAX_COHERENCE, 100)

        self.assertEqual(round(c._QUESTS_REQUIED, 5), 496.34043)
        self.assertEqual(c.COMPANIONS_COHERENCE_EXP_PER_QUEST, 10)

        self.assertEqual(c.COMPANIONS_MEDIUM_COHERENCE, 50)

        self.assertEqual(c.COMPANIONS_MIN_HEALTH, 30)
        self.assertEqual(c.COMPANIONS_MAX_HEALTH, 70)

        self.assertEqual(c._COMPANIONS_MEDIUM_HEALTH, 50)

        self.assertEqual(c._COMPANIONS_MEDIUM_LIFETYME, 15)

        self.assertEqual(c.COMPANIONS_BLOCK_MULTIPLIER_COHERENCE_DELTA, 0.2)
        self.assertEqual(c.COMPANIONS_BLOCK_MULTIPLIER_COMPANION_DEDICATION_DELTA, 0.2)
        self.assertEqual(c.COMPANIONS_BLOCK_MULTIPLIER_HERO_DEDICATION_DELTA, 0.2)

        self.assertEqual(c.COMPANIONS_HABITS_DELTA, 0.5)

        self.assertEqual(c.COMPANIONS_DEFEND_PROBABILITY, 0.1875)

        self.assertEqual(round(c.COMPANIONS_WOUNDS_IN_HOUR_FROM_HEAL, 5), 1.5)
        self.assertEqual(round(c.COMPANIONS_WOUNDS_IN_HOUR_FROM_WOUNDS, 5), 0.13889)

        self.assertEqual(round(c.COMPANIONS_WOUNDS_IN_HOUR, 5), 1.63889)
        self.assertEqual(round(c.COMPANIONS_WOUND_ON_DEFEND_PROBABILITY_FROM_WOUNDS, 5), 0.00604)

        self.assertEqual(c.COMPANIONS_HEALS_IN_HOUR, 1.5)

        self.assertEqual(c.COMPANIONS_HEALTH_PER_HEAL, 1)
        self.assertEqual(c.COMPANIONS_DAMAGE_PER_WOUND, 1)

        self.assertEqual(c.COMPANIONS_HEAL_AMOUNT, 2)
        self.assertEqual(c.COMPANIONS_HEAL_CRIT_AMOUNT, 4)

        self.assertEqual(c.COMPANIONS_BATTLE_STRIKE_PROBABILITY, 0.05)

        self.assertEqual(c.COMPANIONS_EXP_PER_MOVE_GET_EXP, 1)
        self.assertEqual(c.COMPANIONS_GET_EXP_MOVE_EVENTS_PER_HOUR, 2.0)
        self.assertEqual(round(c.COMPANIONS_EXP_PER_MOVE_PROBABILITY, 5), 0.15957)
        self.assertEqual(c.MOVE_TURNS_IN_ACTION_CYCLE, 24)
        self.assertEqual(round(c.MOVE_TURNS_IN_HOUR, 5), 12.53333)

        self.assertEqual(c.COMPANIONS_EXP_PER_HEAL, 1)

        self.assertEqual(c.COMPANIONS_HEAL_BONUS, 0.25)

        self.assertEqual(round(c.COMPANIONS_REGEN_PER_HOUR, 5), 0.03472)

        self.assertEqual(c.COMPANIONS_EATEN_CORPSES_HEAL_AMOUNT, 1)
        self.assertEqual(c.COMPANIONS_REGEN_ON_HEAL_AMOUNT, 2)
        self.assertEqual(c.COMPANIONS_REGEN_BY_HERO, 2)
        self.assertEqual(c.COMPANIONS_REGEN_BY_MONEY_SPEND, 1)

        self.assertEqual(round(c.COMPANIONS_EATEN_CORPSES_PER_BATTLE, 5), 0.00227)
        self.assertEqual(round(c.COMPANIONS_REGEN_ON_HEAL_PER_HEAL, 5), 0.01157)
        self.assertEqual(round(c.COMPANIONS_HERO_REGEN_ON_HEAL_PER_HEAL, 5), 0.01157)

        self.assertEqual(c.COMPANIONS_GIVE_COMPANION_AFTER, 24)

        self.assertEqual(c.COMPANIONS_LEAVE_IN_PLACE, 0.05)

        self.assertEqual(c.COMPANIONS_BONUS_DAMAGE_PROBABILITY, 0.25)


    def test_dedication_maximum_multiplier(self):
        multiplier = ((1 + c.COMPANIONS_BLOCK_MULTIPLIER_COHERENCE_DELTA) *
                      (1 + c.COMPANIONS_BLOCK_MULTIPLIER_COMPANION_DEDICATION_DELTA) *
                      (1 + c.COMPANIONS_BLOCK_MULTIPLIER_HERO_DEDICATION_DELTA))
        self.assertTrue(multiplier < 1.3**3+0.00001)


    def test_energy_regeneration_vs_companion_heal(self):
        energy_in_day = c._ANGEL_ENERGY_IN_DAY

        health_in_day = c.COMPANIONS_WOUNDS_IN_HOUR_FROM_WOUNDS * c.COMPANIONS_DAMAGE_PER_WOUND * 24

        energy_to_heal_in_day = health_in_day / c.COMPANIONS_HEAL_AMOUNT  * c.ANGEL_HELP_COST
        self.assertEqual(round(energy_to_heal_in_day / energy_in_day, 5), 0.13889)
