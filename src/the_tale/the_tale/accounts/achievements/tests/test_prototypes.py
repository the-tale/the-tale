# coding: utf-8

from dext.common.utils.urls import url

from the_tale.common.utils import testcase

from the_tale.accounts.logic import get_system_user

from the_tale.accounts.personal_messages import logic as pm_logic
from the_tale.accounts.personal_messages.tests import helpers as pm_helpers

from the_tale.collections.prototypes import CollectionPrototype, KitPrototype, ItemPrototype, GiveItemTaskPrototype

from the_tale.accounts.achievements.relations import ACHIEVEMENT_GROUP, ACHIEVEMENT_TYPE
from the_tale.accounts.achievements.prototypes import AchievementPrototype, AccountAchievementsPrototype
from the_tale.accounts.achievements.storage import achievements_storage
from the_tale.accounts.achievements import exceptions


from the_tale.game.logic import create_test_map


class AchievementPrototypeTests(testcase.TestCase, pm_helpers.Mixin):

    def setUp(self):
        super(AchievementPrototypeTests, self).setUp()

        self.achievement_1 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=1, points=10,
                                                         caption='achievement_1', description='description_1', approved=True)
        self.achievement_2 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=2, points=10,
                                                         caption='achievement_2', description='description_2', approved=False)
        self.achievement_3 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.TIME, type=ACHIEVEMENT_TYPE.TIME, barrier=3, points=10,
                                                         caption='achievement_3', description='description_3', approved=True)

        pm_logic.debug_clear_service()


    def test_create(self):
        self.assertEqual(set((a.id for a in achievements_storage.all())),
                         set((self.achievement_1.id, self.achievement_2.id, self.achievement_3.id)))


    def test_save(self):
        with self.check_changed(lambda: achievements_storage._version):
            self.achievement_2.save()

    def test_save__exception_when_saved_not_stoage_model(self):
        self.assertRaises(exceptions.SaveNotRegisteredAchievementError, AchievementPrototype.get_by_id(self.achievement_1.id).save)



class AccountAchievementsPrototypeTests(testcase.TestCase, pm_helpers.Mixin):

    def setUp(self):
        super(AccountAchievementsPrototypeTests, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.collection_1 = CollectionPrototype.create(caption='collection_1', description='description_1', approved=True)
        self.kit_1 = KitPrototype.create(collection=self.collection_1, caption='kit_1', description='description_1', approved=True)
        self.item_1_1 = ItemPrototype.create(kit=self.kit_1, caption='item_1_1', text='text_1_1', approved=False)
        self.item_1_2 = ItemPrototype.create(kit=self.kit_1, caption='item_1_2', text='text_1_2', approved=True)
        self.item_1_3 = ItemPrototype.create(kit=self.kit_1, caption='item_1_3', text='text_1_3', approved=True)


        self.achievement_1 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=1, points=10,
                                                         caption='achievement_1', description='description_1', approved=True,
                                                         item_1=self.item_1_1, item_2=self.item_1_2)
        self.achievement_2 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.MONEY, type=ACHIEVEMENT_TYPE.MONEY, barrier=2, points=10,
                                                         caption='achievement_2', description='description_2', approved=False)
        self.achievement_3 = AchievementPrototype.create(group=ACHIEVEMENT_GROUP.TIME, type=ACHIEVEMENT_TYPE.TIME, barrier=3, points=10,
                                                         caption='achievement_3', description='description_3', approved=True)

        self.account_achievements_1 = AccountAchievementsPrototype.get_by_account_id(self.account_1.id)

    def add_achievement__items(self):
        with self.check_delta(GiveItemTaskPrototype._db_count, 2):
            self.account_achievements_1.add_achievement(self.achievement_1, notify=True)

        item_task_1 = GiveItemTaskPrototype._db_get_object(0)
        self.assertEqual(item_task_1.account_id, self.account_1.id)
        self.assertEqual(item_task_1.item_id, self.item_1_1.id)

        item_task_2 = GiveItemTaskPrototype._db_get_object(0)
        self.assertEqual(item_task_2.account_id, self.account_1.id)
        self.assertEqual(item_task_2.item_id, self.item_1_2.id)

    def test_add_achievement__notify(self):
        with self.check_delta(GiveItemTaskPrototype._db_count, 2):
            with self.check_new_message(self.account_1.id, [get_system_user().id]):
                self.account_achievements_1.add_achievement(self.achievement_1, notify=True)


    def test_add_achievement__does_not_notify_when_already_has_achievement(self):
        with self.check_delta(GiveItemTaskPrototype._db_count, 2):
            with self.check_no_messages(self.account_1.id):
                self.account_achievements_1.add_achievement(self.achievement_1, notify=False)

        with self.check_delta(GiveItemTaskPrototype._db_count, 2):
            with self.check_no_messages(self.account_1.id):
                self.account_achievements_1.add_achievement(self.achievement_1, notify=True)


    def test_add_achievement__notify_false(self):
        with self.check_delta(GiveItemTaskPrototype._db_count, 2):
            with self.check_no_messages(self.account_1.id):
                self.account_achievements_1.add_achievement(self.achievement_1, notify=False)

    def test_check(self):
        self.achievement_1.barrier = 2

        self.assertTrue(self.achievement_1.check(1, 3))
        self.assertFalse(self.achievement_1.check(3, 1))
        self.assertFalse(self.achievement_1.check(-1, -3))
        self.assertFalse(self.achievement_1.check(-3, -1))
        self.assertFalse(self.achievement_1.check(1, -1))
        self.assertFalse(self.achievement_1.check(-1, 1))

        self.achievement_1.barrier = -2

        self.assertFalse(self.achievement_1.check(1, 3))
        self.assertFalse(self.achievement_1.check(3, 1))
        self.assertTrue(self.achievement_1.check(-1, -3))
        self.assertFalse(self.achievement_1.check(-3, -1))
        self.assertFalse(self.achievement_1.check(1, -1))
        self.assertFalse(self.achievement_1.check(-1, 1))

        self.achievement_1.barrier = 0

        self.assertFalse(self.achievement_1.check(1, 3))
        self.assertFalse(self.achievement_1.check(3, 1))
        self.assertFalse(self.achievement_1.check(-1, -3))
        self.assertFalse(self.achievement_1.check(-3, -1))
        self.assertTrue(self.achievement_1.check(1, -1))
        self.assertTrue(self.achievement_1.check(-1, 1))
