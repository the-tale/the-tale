# coding: utf-8

from dext.utils.urls import url

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user, get_system_user
from the_tale.accounts.personal_messages.prototypes import MessagePrototype

from the_tale.accounts.achievements.relations import ACHIEVEMENT_GROUP, ACHIEVEMENT_TYPE
from the_tale.accounts.achievements.prototypes import AchievementPrototype, AccountAchievementsPrototype
from the_tale.accounts.achievements.storage import achievements_storage
from the_tale.accounts.achievements import exceptions


from the_tale.game.logic import create_test_map


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



class AccountAchievementsPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(AccountAchievementsPrototypeTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)

        self.achievement_1 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=1, points=10,
                                                         caption=u'achievement_1', description=u'description_1', approved=True)
        self.achievement_2 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=2, points=10,
                                                         caption=u'achievement_2', description=u'description_2', approved=False)
        self.achievement_3 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.TIME, type=ACHIEVEMENT_TYPE.TIME, barrier=3, points=10,
                                                         caption=u'achievement_3', description=u'description_3', approved=True)

        self.account_achievements_1 = AccountAchievementsPrototype.get_by_account_id(self.account_1.id)

    def test_add_achievement__notify(self):
        with self.check_delta(MessagePrototype._db_count, 1):
            self.account_achievements_1.add_achievement(self.achievement_1, notify=True)

        message = MessagePrototype._db_get_object(0)
        self.assertEqual(message.sender_id, get_system_user().id)
        self.assertEqual(message.recipient_id, self.account_1.id)
        self.assertTrue((url('accounts:achievements:group', self.achievement_1.group.slug) + ('#a%d' % self.achievement_1.id)) in
                        message.text)

    def test_add_achievement__notify_false(self):
        with self.check_not_changed(MessagePrototype._db_count):
            self.account_achievements_1.add_achievement(self.achievement_1, notify=False)
