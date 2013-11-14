# coding: utf-8

import mock

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user
from the_tale.accounts.achievements.relations import ACHIEVEMENT_TYPE

from the_tale.game.logic import create_test_map

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.heroes.relations import MONEY_SOURCE


class HeroStatisticsTest(TestCase):

    def setUp(self):
        super(HeroStatisticsTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

        self.hero.statistics.change_money(MONEY_SOURCE.EARNED_FROM_LOOT, 10)
        self.hero.statistics.change_artifacts_had(11)
        self.hero.statistics.change_quests_done(12)
        self.hero.statistics.change_pve_kills(13)
        self.hero.statistics.change_pve_deaths(14)


    def test_change_money__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_money(MONEY_SOURCE.SPEND_FOR_HEAL, 666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.MONEY,
                                                                        object=None,
                                                                        old_value=10,
                                                                        new_value=10)])


        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_money(MONEY_SOURCE.EARNED_FROM_LOOT, 666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.MONEY,
                                                                        object=None,
                                                                        old_value=10,
                                                                        new_value=10+666)])


    def test_change_artifacts_had__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_artifacts_had(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.ARTIFACTS,
                                                                        object=None,
                                                                        old_value=11,
                                                                        new_value=11+666)])


    def test_change_quests_done__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_quests_done(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.QUESTS,
                                                                        object=None,
                                                                        old_value=12,
                                                                        new_value=12+666)])


    def test_change_pve_kills__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_pve_kills(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.MOBS,
                                                                        object=None,
                                                                        old_value=13,
                                                                        new_value=13+666)])


    def test_change_pve_deaths__achievements(self):

        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.hero.statistics.change_pve_deaths(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(self.hero.account_id,
                                                                        type=ACHIEVEMENT_TYPE.DEATHS,
                                                                        object=None,
                                                                        old_value=14,
                                                                        new_value=14+666)])
