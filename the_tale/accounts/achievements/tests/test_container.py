# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.accounts.achievements.relations import ACHIEVEMENT_GROUP, ACHIEVEMENT_TYPE
from the_tale.accounts.achievements.prototypes import AchievementPrototype
from the_tale.accounts.achievements.container import AchievementsContainer


class ContainerTests(testcase.TestCase):

    def setUp(self):
        super(ContainerTests, self).setUp()

        self.achievement_1 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=0, points=10,
                                                         caption=u'achievement_1', description=u'description_1', approved=True)
        self.achievement_2 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=4, points=20,
                                                         caption=u'achievement_2', description=u'description_2', approved=False)
        self.achievement_3 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.TIME, type=ACHIEVEMENT_TYPE.TIME, barrier=8, points=30,
                                                         caption=u'achievement_3', description=u'description_3', approved=True)

        self.container = AchievementsContainer()


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
