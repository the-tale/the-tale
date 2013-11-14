# coding: utf-8

from the_tale.common.utils import testcase
from the_tale.common.utils.permissions import sync_group

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user
from the_tale.accounts.achievements.relations import ACHIEVEMENT_GROUP, ACHIEVEMENT_TYPE
from the_tale.accounts.achievements.prototypes import AchievementPrototype, AccountAchievementsPrototype, GiveAchievementTaskPrototype
from the_tale.accounts.achievements.workers.environment import workers_environment


from the_tale.game.logic import create_test_map



class AchievementsManagerTests(testcase.TestCase):

    def setUp(self):
        super(AchievementsManagerTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

        group_edit = sync_group('edit achievement', ['achievements.edit_achievement'])

        group_edit.user_set.add(self.account_2._model)

        self.achievement_1 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=0,
                                                         caption=u'achievement_1', description=u'description_1', approved=True)
        self.achievement_2 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=5,
                                                         caption=u'achievement_2', description=u'description_2', approved=False)
        self.achievement_3 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.TIME, type=ACHIEVEMENT_TYPE.TIME, barrier=4,
                                                         caption=u'achievement_3', description=u'description_3', approved=True)


        self.account_achievements_1 = AccountAchievementsPrototype.get_by_account_id(self.account_1.id)
        self.account_achievements_1.achievements.add_achievement(self.achievement_1)
        self.account_achievements_1.save()

        self.worker = workers_environment.achievements_manager
        self.worker.initialize()

    def test_add_achievements__not_tasks(self):
        self.worker.add_achievements()
        self.account_achievements_1.reload()
        self.assertEqual(len(self.account_achievements_1.achievements), 1)

    def test_add_achievements(self):
        GiveAchievementTaskPrototype.create(account_id=self.account_1.id, achievement_id=self.achievement_3.id)
        self.assertFalse(self.account_achievements_1.has_achievement(self.achievement_3))
        self.worker.add_achievements()
        self.account_achievements_1.reload()
        self.assertTrue(self.account_achievements_1.has_achievement(self.achievement_3))
        self.assertEqual(GiveAchievementTaskPrototype._db_count(), 0)
