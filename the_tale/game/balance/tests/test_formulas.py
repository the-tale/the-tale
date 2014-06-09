# coding: utf-8
from the_tale.common.utils import testcase

from the_tale.game.balance import formulas as f, constants as c

E = 0.00001


class FormulasTest(testcase.TestCase):

    LVLS = [1, 2, 3, 4, 5, 7, 11, 17, 19, 25, 30, 40, 60, 71, 82, 99, 101]

    def test_lvl_after_time(self):
        for lvl in self.LVLS:
            # print lvl, f.total_time_for_lvl(lvl), f.lvl_after_time(f.total_time_for_lvl(lvl))
            self.assertEqual(lvl, f.lvl_after_time(f.total_time_for_lvl(lvl)))


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
        self.assertEqual(int(f.experience_for_quest__real(100)), 48)

    def test_person_power_for_quest(self):
        self.assertTrue(f.person_power_for_quest(100) < f.person_power_for_quest(1000)< f.person_power_for_quest(10000))
        self.assertEqual(int(f.person_power_for_quest__real(100)), 572)



# if one of this tests broken, we MUST review appropriate achievements' barriers
class AchievementsBarriers(testcase.TestCase):

    def money_after_months(self, months):
        return f.total_gold_at_lvl(f.lvl_after_time(months*30*24))

    def check_money(self, months, money):
        # print months, self.money_after_months(months) , self.money_after_months(months+0.25)
        self.assertTrue(self.money_after_months(months) <= money <= self.money_after_months(months+0.25))

    def test_money(self):
        self.check_money(0.03, 1000)
        self.check_money(0.3, 10000)
        self.check_money(0.9, 50000)
        self.check_money(4.8, 500000)
        self.check_money(7.8, 1000000)
        self.check_money(23, 5000000)


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
        return int((c.ARTIFACTS_LOOT_PER_DAY * months*30-1) * MAGIC)

    def check_artifacts(self, months, artifacts):
        # print self.artifacts_after_months(months), artifacts, self.artifacts_after_months(months+0.25)
        self.assertTrue(self.artifacts_after_months(months) <= artifacts <= self.artifacts_after_months(months+0.25))

    def test_artifacts(self):
        self.check_artifacts(0, 1)
        self.check_artifacts(1, 50)
        self.check_artifacts(2.2, 100)
        self.check_artifacts(5.5, 250)
        self.check_artifacts(11, 500)
        self.check_artifacts(16.5, 750)

    def test_habits(self):
        self.assertEqual(c.HABITS_RIGHT_BORDERS, [-700, -300, -100, 100, 300, 700, 1001])
