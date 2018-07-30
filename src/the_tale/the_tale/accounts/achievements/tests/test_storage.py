
import smart_imports

smart_imports.all()


class StorageTests(utils_testcase.TestCase):

    def setUp(self):
        super(StorageTests, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.achievement_1 = prototypes.AchievementPrototype.create(group=relations.ACHIEVEMENT_GROUP.MONEY, type=relations.ACHIEVEMENT_TYPE.MONEY, barrier=0, points=10,
                                                                    caption='achievement_1', description='description_1', approved=True)
        self.achievement_2 = prototypes.AchievementPrototype.create(group=relations.ACHIEVEMENT_GROUP.MONEY, type=relations.ACHIEVEMENT_TYPE.MONEY, barrier=1, points=10,
                                                                    caption='achievement_2', description='description_2', approved=False)
        self.achievement_3 = prototypes.AchievementPrototype.create(group=relations.ACHIEVEMENT_GROUP.MONEY, type=relations.ACHIEVEMENT_TYPE.MONEY, barrier=2, points=10,
                                                                    caption='achievement_3', description='description_3', approved=True)
        self.achievement_4 = prototypes.AchievementPrototype.create(group=relations.ACHIEVEMENT_GROUP.MONEY, type=relations.ACHIEVEMENT_TYPE.MONEY, barrier=3, points=10,
                                                                    caption='achievement_4', description='description_4', approved=True)
        self.achievement_5 = prototypes.AchievementPrototype.create(group=relations.ACHIEVEMENT_GROUP.MONEY, type=relations.ACHIEVEMENT_TYPE.MONEY, barrier=4, points=10,
                                                                    caption='achievement_5', description='description_5', approved=True)
        self.achievement_6 = prototypes.AchievementPrototype.create(group=relations.ACHIEVEMENT_GROUP.TIME, type=relations.ACHIEVEMENT_TYPE.TIME, barrier=2, points=10,
                                                                    caption='achievement_6', description='description_6', approved=True)

    def test_create(self):
        self.assertEqual(len(storage.achievements.all()), 6)

    def test_by_group(self):
        self.assertEqual(set((a.id for a in storage.achievements.by_group(relations.ACHIEVEMENT_GROUP.DEATHS, only_approved=False))), set())
        self.assertEqual(set((a.id for a in storage.achievements.by_group(relations.ACHIEVEMENT_GROUP.DEATHS, only_approved=True))), set())

        self.assertEqual(set((a.id for a in storage.achievements.by_group(relations.ACHIEVEMENT_GROUP.MONEY, only_approved=False))), set((self.achievement_1.id,
                                                                                                                                          self.achievement_2.id,
                                                                                                                                          self.achievement_3.id,
                                                                                                                                          self.achievement_4.id,
                                                                                                                                          self.achievement_5.id)))
        self.assertEqual(set((a.id for a in storage.achievements.by_group(relations.ACHIEVEMENT_GROUP.MONEY, only_approved=True))), set((self.achievement_1.id,
                                                                                                                                         self.achievement_3.id,
                                                                                                                                         self.achievement_4.id,
                                                                                                                                         self.achievement_5.id)))

        self.assertEqual(set((a.id for a in storage.achievements.by_group(relations.ACHIEVEMENT_GROUP.TIME, only_approved=False))), set((self.achievement_6.id,)))
        self.assertEqual(set((a.id for a in storage.achievements.by_group(relations.ACHIEVEMENT_GROUP.TIME, only_approved=True))), set((self.achievement_6.id,)))

    def test_by_type(self):
        self.assertEqual(set((a.id for a in storage.achievements.by_type(relations.ACHIEVEMENT_TYPE.DEATHS, only_approved=False))), set())
        self.assertEqual(set((a.id for a in storage.achievements.by_type(relations.ACHIEVEMENT_TYPE.DEATHS, only_approved=True))), set())

        self.assertEqual(set((a.id for a in storage.achievements.by_type(relations.ACHIEVEMENT_TYPE.MONEY, only_approved=False))), set((self.achievement_1.id,
                                                                                                                                        self.achievement_2.id,
                                                                                                                                        self.achievement_3.id,
                                                                                                                                        self.achievement_4.id,
                                                                                                                                        self.achievement_5.id)))
        self.assertEqual(set((a.id for a in storage.achievements.by_type(relations.ACHIEVEMENT_TYPE.MONEY, only_approved=True))), set((self.achievement_1.id,
                                                                                                                                       self.achievement_3.id,
                                                                                                                                       self.achievement_4.id,
                                                                                                                                       self.achievement_5.id)))

        self.assertEqual(set((a.id for a in storage.achievements.by_type(relations.ACHIEVEMENT_TYPE.TIME, only_approved=False))), set((self.achievement_6.id,)))
        self.assertEqual(set((a.id for a in storage.achievements.by_type(relations.ACHIEVEMENT_TYPE.TIME, only_approved=True))), set((self.achievement_6.id,)))

    def test_verify_achievements(self):

        with self.check_not_changed(prototypes.GiveAchievementTaskPrototype._db_count):
            storage.achievements.verify_achievements(self.account_1.id,
                                                     type=relations.ACHIEVEMENT_TYPE.MONEY,
                                                     old_value=self.achievement_2.barrier - 1,
                                                     new_value=self.achievement_2.barrier)

        with self.check_delta(prototypes.GiveAchievementTaskPrototype._db_count, 1):
            storage.achievements.verify_achievements(self.account_1.id,
                                                     type=relations.ACHIEVEMENT_TYPE.MONEY,
                                                     old_value=self.achievement_5.barrier - 1,
                                                     new_value=self.achievement_5.barrier)

        give_achievement_task = prototypes.GiveAchievementTaskPrototype._db_get_object(0)

        self.assertEqual(give_achievement_task.achievement_id, self.achievement_5.id)

    def test_verify_achievements__multiple_achievements(self):

        with self.check_delta(prototypes.GiveAchievementTaskPrototype._db_count, 2):
            storage.achievements.verify_achievements(self.account_1.id,
                                                     type=relations.ACHIEVEMENT_TYPE.MONEY,
                                                     old_value=0,
                                                     new_value=self.achievement_4.barrier)
