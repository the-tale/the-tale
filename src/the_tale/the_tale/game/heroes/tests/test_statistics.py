
import smart_imports

smart_imports.all()


class HeroStatisticsTest(utils_testcase.TestCase):

    def setUp(self):
        super(HeroStatisticsTest, self).setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account)
        self.hero = self.storage.accounts_to_heroes[account.id]

        self.hero.statistics.change_money(relations.MONEY_SOURCE.EARNED_FROM_LOOT, 10)
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
            self.hero.statistics.change_money(relations.MONEY_SOURCE.SPEND_FOR_HEAL, 666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.MONEY,
                                                                        old_value=10,
                                                                        new_value=10)])

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_money(relations.MONEY_SOURCE.EARNED_FROM_LOOT, 666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.MONEY,
                                                                        old_value=10,
                                                                        new_value=10 + 666)])

    def test_change_artifacts_had__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_artifacts_had(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.ARTIFACTS,
                                                                        old_value=11,
                                                                        new_value=11 + 666)])

    def test_change_quests_done__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_quests_done(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.QUESTS,
                                                                        old_value=12,
                                                                        new_value=12 + 666)])

    def test_change_pve_kills__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_pve_kills(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.MOBS,
                                                                        old_value=13,
                                                                        new_value=13 + 666)])

    def test_change_pve_deaths__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_pve_deaths(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.DEATHS,
                                                                        old_value=14,
                                                                        new_value=14 + 666)])

    def test_change_pvp_battles_1x1_victories__achievements(self):

        self.assertTrue(self.hero.statistics.pvp_battles_1x1_number < conf.settings.MIN_PVP_BATTLES)

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_pvp_battles_1x1_victories(1)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(new_value=0,
                                                                        old_value=0,
                                                                        account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.PVP_VICTORIES_1X1),
                                                              mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.PVP_BATTLES_1X1,
                                                                        old_value=16,
                                                                        new_value=16 + 1)])

        self.hero.statistics.change_pvp_battles_1x1_defeats(conf.settings.MIN_PVP_BATTLES)

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_pvp_battles_1x1_victories(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.PVP_VICTORIES_1X1,
                                                                        old_value=int(float(17) / (17 + conf.settings.MIN_PVP_BATTLES) * 100),
                                                                        new_value=int(float(17 + 666) / self.hero.statistics.pvp_battles_1x1_number * 100)),
                                                              mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.PVP_BATTLES_1X1,
                                                                        old_value=16 + 1 + conf.settings.MIN_PVP_BATTLES,
                                                                        new_value=16 + 1 + conf.settings.MIN_PVP_BATTLES + 666)])

    def test_change_pvp_battles_1x1_draws__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_pvp_battles_1x1_draws(1)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.PVP_BATTLES_1X1,
                                                                        old_value=16,
                                                                        new_value=16 + 1)])

    def test_change_pvp_battles_1x1_defeats__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_pvp_battles_1x1_defeats(1)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.PVP_BATTLES_1X1,
                                                                        old_value=16,
                                                                        new_value=16 + 1)])

    def test_change_help_count__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_help_count(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.KEEPER_HELP_COUNT,
                                                                        old_value=17,
                                                                        new_value=17 + 666)])

    def test_change_cards_used__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_cards_used(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.KEEPER_CARDS_USED,
                                                                        old_value=18,
                                                                        new_value=18 + 666)])

    def test_change_cards_combined__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_cards_combined(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.hero.account_id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.KEEPER_CARDS_COMBINED,
                                                                        old_value=19,
                                                                        new_value=19 + 666)])

    def test_change_giftst_used__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_gifts_returned(666)

        self.assertEqual(verify_achievements.call_args_list, [])

    @mock.patch('the_tale.game.heroes.conf.settings.MIN_PVP_BATTLES', 1000)
    def test_change_pvp_battles_1x1_victories__multiple_victories_achievements(self):

        achievement_1 = achievements_prototypes.AchievementPrototype.create(group=achievements_relations.ACHIEVEMENT_GROUP.MONEY, type=achievements_relations.ACHIEVEMENT_TYPE.PVP_VICTORIES_1X1, barrier=10, points=10,
                                                                            caption='achievement_1', description='description_1', approved=True)
        achievement_2 = achievements_prototypes.AchievementPrototype.create(group=achievements_relations.ACHIEVEMENT_GROUP.MONEY, type=achievements_relations.ACHIEVEMENT_TYPE.PVP_VICTORIES_1X1, barrier=20, points=10,
                                                                            caption='achievement_2', description='description_2', approved=True)
        achievement_3 = achievements_prototypes.AchievementPrototype.create(group=achievements_relations.ACHIEVEMENT_GROUP.MONEY, type=achievements_relations.ACHIEVEMENT_TYPE.PVP_VICTORIES_1X1, barrier=30, points=10,
                                                                            caption='achievement_3', description='description_3', approved=True)
        achievement_4 = achievements_prototypes.AchievementPrototype.create(group=achievements_relations.ACHIEVEMENT_GROUP.MONEY, type=achievements_relations.ACHIEVEMENT_TYPE.PVP_VICTORIES_1X1, barrier=40, points=10,
                                                                            caption='achievement_4', description='description_4', approved=True)

        self.assertEqual(self.hero.statistics.pvp_battles_1x1_number, 16)

        with self.check_not_changed(achievements_prototypes.GiveAchievementTaskPrototype._db_count):
            self.hero.statistics.change_pvp_battles_1x1_draws(400)
            self.hero.statistics.change_pvp_battles_1x1_defeats(300)

        with self.check_delta(achievements_prototypes.GiveAchievementTaskPrototype._db_count, 3):
            self.hero.statistics.change_pvp_battles_1x1_victories(300)

        self.assertEqual(set(achievements_prototypes.GiveAchievementTaskPrototype._db_all().values_list('achievement_id', flat=True)),
                         set([achievement_1.id, achievement_2.id, achievement_3.id]))

        with self.check_delta(achievements_prototypes.GiveAchievementTaskPrototype._db_count, 1):
            self.hero.statistics.change_pvp_battles_1x1_victories(200)

        self.assertEqual(set(achievements_prototypes.GiveAchievementTaskPrototype._db_all().values_list('achievement_id', flat=True)),
                         set([achievement_1.id, achievement_2.id, achievement_3.id, achievement_4.id]))

        self.assertEqual(self.hero.statistics.pvp_battles_1x1_number, 1216)
        self.assertEqual(self.hero.statistics.pvp_battles_1x1_victories, 516)
        self.assertEqual(self.hero.statistics.pvp_battles_1x1_defeats, 300)
        self.assertEqual(self.hero.statistics.pvp_battles_1x1_draws, 400)
