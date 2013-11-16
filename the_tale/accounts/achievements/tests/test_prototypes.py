# coding: utf-8


from the_tale.common.utils import testcase

from the_tale.accounts.achievements.relations import ACHIEVEMENT_GROUP, ACHIEVEMENT_TYPE
from the_tale.accounts.achievements.prototypes import AchievementPrototype
from the_tale.accounts.achievements.storage import achievements_storage
from the_tale.accounts.achievements import exceptions


class AchievementPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(AchievementPrototypeTests, self).setUp()

        self.achievement_1 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=1, points=10,
                                                         caption=u'achievement_1', description=u'description_1', approved=True)
        self.achievement_2 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=2, points=10,
                                                         caption=u'achievement_2', description=u'description_2', approved=False)
        self.achievement_3 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.TIME, type=ACHIEVEMENT_TYPE.TIME, barrier=3, points=10,
                                                         caption=u'achievement_3', description=u'description_3', approved=True)


    def test_create(self):
        self.assertEqual(set((a.id for a in achievements_storage.all())),
                         set((self.achievement_1.id, self.achievement_2.id, self.achievement_3.id)))


    def test_save(self):
        with self.check_changed(lambda: achievements_storage._version):
            self.achievement_2.save()

    def test_save__exception_when_saved_not_stoage_model(self):
        self.assertRaises(exceptions.SaveNotRegisteredAchievementError, AchievementPrototype.get_by_id(self.achievement_1.id).save)
