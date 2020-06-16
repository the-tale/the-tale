
import smart_imports

smart_imports.all()


E = 0.00001


class FormulasTest(utils_testcase.TestCase):

    LVLS = [1, 2, 3, 4, 5, 7, 11, 17, 19, 25, 30, 40, 60, 71, 82, 99, 101]

    def test_experience_for_quest(self):
        self.assertTrue(f.experience_for_quest(100) < f.experience_for_quest(1000) < f.experience_for_quest(10000))
        self.assertEqual(int(f.experience_for_quest__real(100)), 152)

    def test_companions_defend_in_battle_probability(self):
        self.assertEqual(round(f.companions_defend_in_battle_probability(0), 5), 0.15)
        self.assertEqual(round(f.companions_defend_in_battle_probability(25), 5), 0.16875)
        self.assertEqual(round(f.companions_defend_in_battle_probability(50), 5), 0.1875)
        self.assertEqual(round(f.companions_defend_in_battle_probability(75), 5), 0.20625)
        self.assertEqual(round(f.companions_defend_in_battle_probability(100), 5), 0.225)

    def test_companions_heal_length(self):
        self.assertEqual(f.companions_heal_length(0, 30), 27)
        self.assertEqual(f.companions_heal_length(15, 30), 18)
        self.assertEqual(f.companions_heal_length(30, 30), 9)

        self.assertEqual(f.companions_heal_length(0, 50), 27)
        self.assertEqual(f.companions_heal_length(25, 50), 18)
        self.assertEqual(f.companions_heal_length(50, 50), 9)

        self.assertEqual(f.companions_heal_length(0, 70), 27)
        self.assertEqual(f.companions_heal_length(35, 70), 18)
        self.assertEqual(f.companions_heal_length(70, 70), 9)

    def test_gold_in_path(self):
        self.assertEqual(f.gold_in_path(10, 100), 1667)

    def test_normal_loot_cost_at_lvl(self):
        self.assertEqual(f.normal_loot_cost_at_lvl(1), 1)
        self.assertEqual(f.normal_loot_cost_at_lvl(10), 9)
        self.assertEqual(f.normal_loot_cost_at_lvl(25), 13)
        self.assertEqual(f.normal_loot_cost_at_lvl(50), 15)
        self.assertEqual(f.normal_loot_cost_at_lvl(100), 18)

    def test_sell_artifact_price(self):
        self.assertEqual(f.sell_artifact_price(1), 31)
        self.assertEqual(f.sell_artifact_price(10), 184)
        self.assertEqual(f.sell_artifact_price(25), 276)
        self.assertEqual(f.sell_artifact_price(50), 338)
        self.assertEqual(f.sell_artifact_price(100), 430)


# if one of this tests broken, we MUST review appropriate achievements' barriers
class AchievementsBarriers(utils_testcase.TestCase):

    def money_after_months(self, months):
        return f.total_gold_at_lvl(f.lvl_after_time(months * 30 * 24))

    def check_money(self, months, money):
        # print months, self.money_after_months(months) , self.money_after_months(months+0.25)
        self.assertTrue(self.money_after_months(months) <= money <= self.money_after_months(months + 0.25))

    def test_money(self):
        self.check_money(0.03, 1000)
        self.check_money(0.3, 10000)
        self.check_money(1.0, 50000)
        self.check_money(6.8, 500000)
        self.check_money(12.8, 1000000)
        self.check_money(27.4, 2500000)

    def mobs_after_months(self, months):
        return int(c.BATTLES_PER_HOUR * months * 30 * 24)

    def check_mobs(self, months, mobs):
        # print months, self.mobs_after_months(months) , self.mobs_after_months(months+0.05)
        self.assertTrue(self.mobs_after_months(months) <= mobs <= self.mobs_after_months(months + 0.05))

    def test_mobs(self):
        self.check_mobs(0.08, 1000)
        self.check_mobs(0.45, 5000)
        self.check_mobs(1.35, 15000)
        self.check_mobs(4.5, 50000)
        self.check_mobs(9.05, 100000)
        self.check_mobs(13.55, 150000)
        self.check_mobs(22.65, 250000)
        self.check_mobs(36.25, 400000)

    def artifacts_after_months(self, months):
        MAGIC = 1.5  # magic cooficient, to spend money events and abilities
        return int(((c.ARTIFACTS_LOOT_PER_DAY + c.EXPECTED_QUESTS_IN_DAY * c.ARTIFACT_FOR_QUEST_PROBABILITY) * months * 30 - 1) * MAGIC)

    def check_artifacts(self, months, artifacts):
        # print months, self.artifacts_after_months(months), artifacts, self.artifacts_after_months(months+0.25)
        self.assertTrue(self.artifacts_after_months(months) <= artifacts <= self.artifacts_after_months(months + 0.25))

    def test_artifacts(self):
        self.check_artifacts(0, 1)
        self.check_artifacts(0.48, 50)
        self.check_artifacts(0.9, 100)
        self.check_artifacts(2.3, 250)
        self.check_artifacts(4.6, 500)
        self.check_artifacts(6.9, 750)

    def test_habits(self):
        self.assertEqual(c.HABITS_RIGHT_BORDERS, [-700, -300, -100, 100, 300, 700, 1001])
