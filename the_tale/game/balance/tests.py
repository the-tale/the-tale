# coding: utf-8

from django.test import TestCase


from . import formulas as f, constants as c


class ConstantsTest(TestCase):

    def test_constants_values(self):

        self.assertEqual(c.TIME_TO_LVL_DELTA, 5.0)
        self.assertEqual(c.INITIAL_HP, 500)
        self.assertEqual(c.HP_PER_LVL, 50)
        self.assertEqual(c.MOB_HP_MULTIPLIER, 0.25)
        self.assertEqual(c.TURN_DELTA, 10)
        self.assertEqual(c.TURNS_IN_HOUR, 360.0)
        self.assertEqual(c.POWER_PER_LVL, 1)
        self.assertEqual(c.EQUIP_SLOTS_NUMBER, 12)
        self.assertEqual(c.ARTIFACTS_PER_LVL, 4)
        self.assertEqual(c.EXP_PER_MOB, 1.0)
        self.assertEqual(c.EXP_MULTIPLICATOR, 10.0)
        self.assertEqual(c.EXP_PENALTY_MULTIPLIER, 3.0)
        self.assertEqual(c.EXP_ACTIVE_STATE_LENGTH, 360.0*2*24)
        self.assertEqual(c.BATTLE_LENGTH, 16)
        self.assertEqual(c.INTERVAL_BETWEEN_BATTLES, 5)
        self.assertEqual(c.BATTLES_BEFORE_HEAL, 8)
        self.assertEqual(c.HEAL_TIME_FRACTION, 0.2)
        self.assertEqual(c.HEAL_STEP_FRACTION, 0.2)

        self.assertEqual(c.HEALTH_IN_SETTLEMENT_TO_START_HEAL_FRACTION, 0.33)
        self.assertEqual(c.HEALTH_IN_MOVE_TO_START_HEAL_FRACTION, 0.25)

        self.assertEqual(c.TURNS_TO_RESURRECT, 20)
        self.assertEqual(c.TURNS_TO_IDLE, 20)


        self.assertEqual(c.GET_LOOT_PROBABILITY, 0.33)
        self.assertEqual(c.NORMAL_LOOT_PROBABILITY, 0.99)
        self.assertEqual(c.RARE_LOOT_PROBABILITY, 0.0099)
        self.assertTrue(c.EPIC_LOOT_PROBABILITY - 0.0001 < 1e-10)
        self.assertEqual(c.NORMAL_LOOT_COST, 1.5)
        self.assertEqual(c.RARE_LOOT_COST, 25.0)
        self.assertEqual(c.EPIC_LOOT_COST, 250.0)
        self.assertEqual(c.NORMAL_ACTION_PRICE_MULTIPLYER, 1.2)
        self.assertEqual(c.INSTANT_HEAL_PRICE_FRACTION, 0.3)
        self.assertEqual(c.BUY_ARTIFACT_PRICE_FRACTION, 1.5)
        self.assertEqual(c.SHARPENING_ARTIFACT_PRICE_FRACTION, 2.0)
        self.assertEqual(c.USELESS_PRICE_FRACTION, 0.4)
        self.assertEqual(c.IMPACT_PRICE_FRACTION, 2.5)
        self.assertEqual(c.SELL_ARTIFACT_PRICE_FRACTION, 0.1)
        self.assertEqual(c.PRICE_DELTA, 0.2)
        self.assertEqual(c.POWER_TO_LVL, 12.0)
        self.assertEqual(c.ARTIFACT_POWER_DELTA, 6)
        self.assertEqual(c.BATTLES_LINE_LENGTH, 8*(16+5)-5)
        self.assertEqual(c.BATTLES_PER_TURN, 1.0 / 5 )
        self.assertEqual(c.HEAL_LENGTH, int((8*(16+5)-5) * 0.2))
        self.assertEqual(c.ACTIONS_CYCLE_LENGTH, int(8*(16+5)-5 + (8*(16+5)-5) * 0.2))
        self.assertEqual(c.BATTLES_PER_HOUR, 360.0 / (int(8*(16+5)-5 + (8*(16+5)-5) * 0.2)) * 8)
        self.assertEqual(c.DAMAGE_TO_HERO_PER_HIT_FRACTION, 1.0 / (8*16/2))
        self.assertEqual(c.DAMAGE_TO_MOB_PER_HIT_FRACTION, 1.0 / (16/2))
        self.assertEqual(c.DAMAGE_DELTA, 0.2)
        self.assertEqual(c.DAMAGE_CRIT_MULTIPLIER, 2.0)
        self.assertEqual(c.EXP_PER_HOUR, (360.0 / (int(8*(16+5)-5 + (8*(16+5)-5) * 0.2)) * 8) * 1)

        self.assertEqual(c.MAX_BAG_SIZE, 12)
        self.assertEqual(c.BAG_SIZE_TO_SELL_LOOT_FRACTION, 0.33)

        self.assertEqual(c.ITEMS_OF_EXPENDITURE_PRIORITY, { c.ITEMS_OF_EXPENDITURE.INSTANT_HEAL: 6,
                                                            c.ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT: 2,
                                                            c.ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT: 2,
                                                            c.ITEMS_OF_EXPENDITURE.USELESS: 1,
                                                            c.ITEMS_OF_EXPENDITURE.IMPACT: 2 } )

        self.assertEqual(c.DESTINY_POINT_IN_LEVELS, 5)

        self.assertEqual(c.ANGEL_ENERGY_MAX, 12)
        self.assertEqual(c.ANGEL_ENERGY_REGENERATION_TIME,  0.5)
        self.assertEqual(c.ANGEL_ENERGY_REGENERATION_PERIOD,  180)
        self.assertEqual(c.ANGEL_ENERGY_REGENERATION_AMAUNT, 1)

        self.assertEqual(c.ANGEL_ENERGY_REGENERATION_DELAY, { c.ANGEL_ENERGY_REGENERATION_TYPES.PRAY: 1,
                                                              c.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE: 2,
                                                              c.ANGEL_ENERGY_REGENERATION_TYPES.INCENSE: 4,
                                                              c.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS: 3,
                                                              c.ANGEL_ENERGY_REGENERATION_TYPES.MEDITATION: 2 })

        self.assertEqual(c.ANGEL_ENERGY_REGENERATION_STEPS, { c.ANGEL_ENERGY_REGENERATION_TYPES.PRAY: 3,
                                                              c.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE: 5,
                                                              c.ANGEL_ENERGY_REGENERATION_TYPES.INCENSE: 6,
                                                              c.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS: 4,
                                                              c.ANGEL_ENERGY_REGENERATION_TYPES.MEDITATION: 4 })

        self.assertEqual(c.ANGEL_HELP_HEAL_IF_LOWER_THEN, float(0.8))
        self.assertEqual(c.ANGEL_HELP_HEAL_FRACTION,  (float(0.25), float(0.5)))
        self.assertEqual(c.ANGEL_HELP_TELEPORT_DISTANCE, float(3.0))
        self.assertEqual(c.ANGEL_HELP_LIGHTING_FRACTION, (float(0.25), float(0.5)))

        self.assertEqual(c.HELP_CHOICES_PRIORITY, { c.HELP_CHOICES.HEAL: 4,
                                                    c.HELP_CHOICES.TELEPORT: 4,
                                                    c.HELP_CHOICES.LIGHTING: 4,
                                                    c.HELP_CHOICES.START_QUEST: 4,
                                                    c.HELP_CHOICES.MONEY: 1,
                                                    c.HELP_CHOICES.RESURRECT: 10,})

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

        self.assertEqual(c.GAME_SECONDS_IN_TURN, 120)

        self.assertEqual(c.MAP_CELL_LENGTH, 3.0)
        self.assertEqual(c.MAP_SYNC_TIME, 1440)

        self.assertEqual(c.QUESTS_SPECIAL_FRACTION, 0.2)

        self.assertEqual(c.QUESTS_LOCK_TIME, { 'hunt': int(1.5*12*360),
                                               'hometown': int(12*360),
                                               'helpfriend': int(12*360),
                                               'interfereenemy': int(12*360),
                                               'searchsmith': int(0.5*12*360) })

        self.assertEqual(c.PERSON_POWER_FOR_QUEST, 100)
        self.assertEqual(c.PERSON_POWER_FOR_RANDOM_SPEND, 10)

        self.assertEqual(c.CHARACTER_PREFERENCES_ENERGY_REGENERATION_TYPE_LEVEL_REQUIRED, 1)
        self.assertEqual(c.CHARACTER_PREFERENCES_PLACE_LEVEL_REQUIRED, 3)
        self.assertEqual(c.CHARACTER_PREFERENCES_MOB_LEVEL_REQUIRED, 7)
        self.assertEqual(c.CHARACTER_PREFERENCES_FRIEND_LEVEL_REQUIRED, 11)
        self.assertEqual(c.CHARACTER_PREFERENCES_ENEMY_LEVEL_REQUIRED, 16)
        self.assertEqual(c.CHARACTER_PREFERENCES_EQUIPMENT_SLOT_LEVEL_REQUIRED, 21)

        self.assertEqual(c.CHARACTER_PREFERENCES_CHANGE_DELAY, 60*60*24*7)



class FormulasTest(TestCase):

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
