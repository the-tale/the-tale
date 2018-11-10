
import smart_imports

smart_imports.all()


class ContainerTests(utils_testcase.TestCase):

    def setUp(self):
        super(ContainerTests, self).setUp()

        self.achievement_1 = prototypes.AchievementPrototype.create(group=relations.ACHIEVEMENT_GROUP.MONEY, type=relations.ACHIEVEMENT_TYPE.MONEY, barrier=0, points=10,
                                                                    caption='achievement_1', description='description_1', approved=True)
        self.achievement_2 = prototypes.AchievementPrototype.create(group=relations.ACHIEVEMENT_GROUP.MONEY, type=relations.ACHIEVEMENT_TYPE.MONEY, barrier=4, points=20,
                                                                    caption='achievement_2', description='description_2', approved=False)
        self.achievement_3 = prototypes.AchievementPrototype.create(group=relations.ACHIEVEMENT_GROUP.TIME, type=relations.ACHIEVEMENT_TYPE.TIME, barrier=8, points=30,
                                                                    caption='achievement_3', description='description_3', approved=True)

        self.container = container.AchievementsContainer()

    def test_add_achievement(self):
        self.assertFalse(self.container.has_achievement(self.achievement_1))
        self.assertFalse(self.container.updated)
        self.assertEqual(self.container.get_points(), 0)
        self.container.add_achievement(self.achievement_1)
        self.assertTrue(self.container.has_achievement(self.achievement_1))
        self.assertTrue(self.container.updated)
        self.assertEqual(self.container.get_points(), 10)

    def test_add_achievement__existed(self):
        self.container.add_achievement(self.achievement_1)
        self.assertEqual(self.container.get_points(), 10)
        old_time = self.container.achievements[self.achievement_1.id]
        self.container.add_achievement(self.achievement_1)
        self.assertEqual(old_time, self.container.achievements[self.achievement_1.id])
        self.assertEqual(self.container.get_points(), 10)

    def test_last_achievements(self):
        self.container.add_achievement(self.achievement_3)
        self.container.add_achievement(self.achievement_2)
        self.container.add_achievement(self.achievement_1)

        self.assertEqual(self.container.last_achievements(number=3), [self.achievement_1, self.achievement_3])
