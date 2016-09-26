# coding: utf-8

import mock

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.achievements.relations import ACHIEVEMENT_TYPE

from the_tale.game.logic import create_test_map

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.heroes.relations import MONEY_SOURCE
from the_tale.game.heroes.conf import heroes_settings


class HeroStatisticsTest(TestCase):

    def setUp(self):
        super(HeroStatisticsTest, self).setUp()

        self.place_1, self.place_2, self.place_3 = create_test_map()

        account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]

        self.hero.statistics.change_money(MONEY_SOURCE.EARNED_FROM_LOOT, 10)
        self.hero.statistics.change_artifacts_had(11)
        self.hero.statistics.change_quests_done(12)
        self.hero.statistics.change_pve_kills(13)
        self.hero.statistics.change_pve_deaths(14)

        self.hero.statistics.change_pvp_battles_1x1_victories(16)
        self.hero.statistics.change_help_count(17)
        self.hero.statistics.change_cards_used(18)
        self.hero.statistics.change_cards_combined(19)

        self.hero.statistics.change_gifts_returned(20)

        self.hero.statistics.change_companions_count(21)

        self.assertEqual(self.hero.statistics.pvp_battles_1x1_number, 16)


    def test_change_money__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_money(MONEY_SOURCE.SPEND_FOR_HEAL, 666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.MONEY,
                                                                        old_value=10,
                                                                        new_value=10)])


        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_money(MONEY_SOURCE.EARNED_FROM_LOOT, 666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.MONEY,
                                                                        old_value=10,
                                                                        new_value=10+666)])


    def test_change_artifacts_had__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_artifacts_had(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.ARTIFACTS,
                                                                        old_value=11,
                                                                        new_value=11+666)])


    def test_change_quests_done__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_quests_done(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.QUESTS,
                                                                        old_value=12,
                                                                        new_value=12+666)])


    def test_change_pve_kills__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_pve_kills(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.MOBS,
                                                                        old_value=13,
                                                                        new_value=13+666)])


    def test_change_pve_deaths__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_pve_deaths(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.DEATHS,
                                                                        old_value=14,
                                                                        new_value=14+666)])


    def test_change_pvp_battles_1x1_victories__achievements(self):

        self.assertTrue(self.hero.statistics.pvp_battles_1x1_number < heroes_settings.MIN_PVP_BATTLES)

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_pvp_battles_1x1_victories(1)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(new_value=0,
                                                                        old_value=0,
                                                                        account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.PVP_VICTORIES_1X1),
                                                              mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.PVP_BATTLES_1X1,
                                                                        old_value=16,
                                                                        new_value=16+1)])

        self.hero.statistics.change_pvp_battles_1x1_defeats(heroes_settings.MIN_PVP_BATTLES)

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_pvp_battles_1x1_victories(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.PVP_VICTORIES_1X1,
                                                                        old_value=int(float(17) / (17 + heroes_settings.MIN_PVP_BATTLES) * 100),
                                                                        new_value=int(float(17+666) / self.hero.statistics.pvp_battles_1x1_number * 100)),
                                                              mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.PVP_BATTLES_1X1,
                                                                        old_value=16+1+heroes_settings.MIN_PVP_BATTLES,
                                                                        new_value=16+1+heroes_settings.MIN_PVP_BATTLES+666)])


    def test_change_pvp_battles_1x1_draws__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_pvp_battles_1x1_draws(1)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.PVP_BATTLES_1X1,
                                                                        old_value=16,
                                                                        new_value=16+1)])


    def test_change_pvp_battles_1x1_defeats__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_pvp_battles_1x1_defeats(1)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.PVP_BATTLES_1X1,
                                                                        old_value=16,
                                                                        new_value=16+1)])



    def test_change_help_count__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_help_count(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.KEEPER_HELP_COUNT,
                                                                        old_value=17,
                                                                        new_value=17+666)])

    def test_change_cards_used__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_cards_used(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.KEEPER_CARDS_USED,
                                                                        old_value=18,
                                                                        new_value=18+666)])


    def test_change_cards_combined__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_cards_combined(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.KEEPER_CARDS_COMBINED,
                                                                        old_value=19,
                                                                        new_value=19+666)])


    def test_change_giftst_used__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_gifts_returned(666)

        self.assertEqual(verify_achievements.call_args_list, [])


    @mock.patch('the_tale.game.heroes.conf.heroes_settings.MIN_PVP_BATTLES', 1000)
    def test_change_pvp_battles_1x1_victories__multiple_victories_achievements(self):
        from the_tale.accounts.achievements.relations import ACHIEVEMENT_GROUP, ACHIEVEMENT_TYPE
        from the_tale.accounts.achievements.prototypes import AchievementPrototype, GiveAchievementTaskPrototype

        achievement_1 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.PVP_VICTORIES_1X1, barrier=10, points=10,
                                    caption='achievement_1', description='description_1', approved=True)
        achievement_2 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.PVP_VICTORIES_1X1, barrier=20, points=10,
                                    caption='achievement_2', description='description_2', approved=True)
        achievement_3 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.PVP_VICTORIES_1X1, barrier=30, points=10,
                                    caption='achievement_3', description='description_3', approved=True)
        achievement_4 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.PVP_VICTORIES_1X1, barrier=40, points=10,
                                    caption='achievement_4', description='description_4', approved=True)


        self.assertEqual(self.hero.statistics.pvp_battles_1x1_number, 16)

        with self.check_not_changed(GiveAchievementTaskPrototype._db_count):
            self.hero.statistics.change_pvp_battles_1x1_draws(400)
            self.hero.statistics.change_pvp_battles_1x1_defeats(300)

        with self.check_delta(GiveAchievementTaskPrototype._db_count, 3):
            self.hero.statistics.change_pvp_battles_1x1_victories(300)

        self.assertEqual(set(GiveAchievementTaskPrototype._db_all().values_list('achievement_id', flat=True)),
                         set([achievement_1.id, achievement_2.id, achievement_3.id]))

        with self.check_delta(GiveAchievementTaskPrototype._db_count, 1):
            self.hero.statistics.change_pvp_battles_1x1_victories(200)

        self.assertEqual(set(GiveAchievementTaskPrototype._db_all().values_list('achievement_id', flat=True)),
                         set([achievement_1.id, achievement_2.id, achievement_3.id, achievement_4.id]))


        self.assertEqual(self.hero.statistics.pvp_battles_1x1_number, 1216)
        self.assertEqual(self.hero.statistics.pvp_battles_1x1_victories, 516)
        self.assertEqual(self.hero.statistics.pvp_battles_1x1_defeats, 300)
        self.assertEqual(self.hero.statistics.pvp_battles_1x1_draws, 400)
