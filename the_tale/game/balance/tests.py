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
        self.assertEqual(c.INSTANT_HEAL_PRICE_FRACTION, 0.3)
        self.assertEqual(c.BUY_ARTIFACT_PRICE_FRACTION, 2.0)
        self.assertEqual(c.SHARPENING_ARTIFACT_PRICE_FRACTION, 1.5)
        self.assertEqual(c.USELESS_PRICE_FRACTION, 0.2)
        self.assertEqual(c.IMPACT_PRICE_FRACTION, 1.5)
        self.assertEqual(c.SELL_ARTIFACT_PRICE_FRACTION, 0.15)
        self.assertEqual(c.PRICE_DELTA, 0.2)
        self.assertEqual(c.POWER_TO_LVL, 12.0)
        self.assertEqual(c.ARTIFACT_POWER_DELTA, 2)
        self.assertEqual(c.BATTLES_LINE_LENGTH, 8*(16+5)-5)
        self.assertEqual(c.BATTLES_PER_TURN, 1.0 / 5 )
        self.assertEqual(c.HEAL_LENGTH, int((8*(16+5)-5) * 0.2))
        self.assertEqual(c.ACTIONS_CYCLE_LENGTH, int(8*(16+5)-5 + (8*(16+5)-5) * 0.2))
        self.assertEqual(c.BATTLES_PER_HOUR, 360.0 / (int(8*(16+5)-5 + (8*(16+5)-5) * 0.2)) * 8)
        self.assertEqual(c.DAMAGE_TO_HERO_PER_HIT_FRACTION, 1.0 / (8*16/2))
        self.assertEqual(c.DAMAGE_TO_MOB_PER_HIT_FRACTION, 1.0 / (16/2))
        self.assertEqual(c.DAMAGE_DELTA, 0.2)
        self.assertEqual(c.EXP_PER_HOUR, (360.0 / (int(8*(16+5)-5 + (8*(16+5)-5) * 0.2)) * 8) * 1)

        self.assertEqual(c.MAX_BAG_SIZE, 12)
        self.assertEqual(c.BAG_SIZE_TO_SELL_LOOT_FRACTION, 0.33)

        self.assertEqual(c.QUEST_REWARD_MONEY_FRACTION, 0.5)
        self.assertEqual(c.QUEST_REWARD_ARTIFACT_FRACTION, 0.5)

        self.assertEqual(c.ANGEL_ENERGY_MAX, 12)
        self.assertEqual(c.ANGEL_ENERGY_REGENERATION_PERIOD,  2*360)
        self.assertEqual(c.ANGEL_ENERGY_REGENERATION_AMAUNT, 1)


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
