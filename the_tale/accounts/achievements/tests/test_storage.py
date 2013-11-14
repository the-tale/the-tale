# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.accounts.achievements.relations import ACHIEVEMENT_GROUP, ACHIEVEMENT_TYPE
from the_tale.accounts.achievements.prototypes import AchievementPrototype, GiveAchievementTaskPrototype
from the_tale.accounts.achievements.storage import achievements_storage

from the_tale.game.logic import create_test_map


class StorageTests(testcase.TestCase):

    def setUp(self):
        super(StorageTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)

        self.achievement_1 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=0,
                                                         caption=u'achievement_1', description=u'description_1', approved=True)
        self.achievement_2 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=1,
                                                         caption=u'achievement_2', description=u'description_2', approved=False)
        self.achievement_3 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=2,
                                                         caption=u'achievement_3', description=u'description_3', approved=True)
        self.achievement_4 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=3,
                                                         caption=u'achievement_4', description=u'description_4', approved=True)
        self.achievement_5 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=4,
                                                         caption=u'achievement_5', description=u'description_5', approved=True)
        self.achievement_6 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.TIME, type=ACHIEVEMENT_TYPE.TIME, barrier=2,
                                                         caption=u'achievement_6', description=u'description_6', approved=True)


    def test_create(self):
        self.assertEqual(len(achievements_storage.all()), 6)


    def test_by_group(self):
        self.assertEqual(set((a.id for a in achievements_storage.by_group(ACHIEVEMENT_GROUP.DEATHS, only_approved=False))), set())
        self.assertEqual(set((a.id for a in achievements_storage.by_group(ACHIEVEMENT_GROUP.DEATHS, only_approved=True))), set())

        self.assertEqual(set((a.id for a in achievements_storage.by_group(ACHIEVEMENT_GROUP.MONEY, only_approved=False))), set((self.achievement_1.id,
                                                                                                                                self.achievement_2.id,
                                                                                                                                self.achievement_3.id,
                                                                                                                                self.achievement_4.id,
                                                                                                                                self.achievement_5.id)))
        self.assertEqual(set((a.id for a in achievements_storage.by_group(ACHIEVEMENT_GROUP.MONEY, only_approved=True))), set((self.achievement_1.id,
                                                                                                                               self.achievement_3.id,
                                                                                                                               self.achievement_4.id,
                                                                                                                               self.achievement_5.id)))

        self.assertEqual(set((a.id for a in achievements_storage.by_group(ACHIEVEMENT_GROUP.TIME, only_approved=False))), set((self.achievement_6.id,)))
        self.assertEqual(set((a.id for a in achievements_storage.by_group(ACHIEVEMENT_GROUP.TIME, only_approved=True))), set((self.achievement_6.id,)))

    def test_by_type(self):
        self.assertEqual(set((a.id for a in achievements_storage.by_type(ACHIEVEMENT_TYPE.DEATHS, only_approved=False))), set())
        self.assertEqual(set((a.id for a in achievements_storage.by_type(ACHIEVEMENT_TYPE.DEATHS, only_approved=True))), set())

        self.assertEqual(set((a.id for a in achievements_storage.by_type(ACHIEVEMENT_TYPE.MONEY, only_approved=False))), set((self.achievement_1.id,
                                                                                                                                self.achievement_2.id,
                                                                                                                                self.achievement_3.id,
                                                                                                                                self.achievement_4.id,
                                                                                                                                self.achievement_5.id)))
        self.assertEqual(set((a.id for a in achievements_storage.by_type(ACHIEVEMENT_TYPE.MONEY, only_approved=True))), set((self.achievement_1.id,
                                                                                                                               self.achievement_3.id,
                                                                                                                               self.achievement_4.id,
                                                                                                                               self.achievement_5.id)))

        self.assertEqual(set((a.id for a in achievements_storage.by_type(ACHIEVEMENT_TYPE.TIME, only_approved=False))), set((self.achievement_6.id,)))
        self.assertEqual(set((a.id for a in achievements_storage.by_type(ACHIEVEMENT_TYPE.TIME, only_approved=True))), set((self.achievement_6.id,)))

    def test_verify_achievements(self):

        with self.check_not_changed(GiveAchievementTaskPrototype._db_count):
            achievements_storage.verify_achievements(self.account_1.id,
                                                     type=ACHIEVEMENT_TYPE.MONEY,
                                                     object=None,
                                                     old_value=self.achievement_2.barrier-1,
                                                     new_value=self.achievement_2.barrier)


        with self.check_delta(GiveAchievementTaskPrototype._db_count, 1):
            achievements_storage.verify_achievements(self.account_1.id,
                                                     type=ACHIEVEMENT_TYPE.MONEY,
                                                     object=None,
                                                     old_value=self.achievement_5.barrier-1,
                                                     new_value=self.achievement_5.barrier)

        give_achievement_task = GiveAchievementTaskPrototype._db_get_object(0)

        self.assertEqual(give_achievement_task.achievement_id, self.achievement_5.id)
