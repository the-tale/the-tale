# coding: utf-8
import mock

import datetime

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map

from the_tale.forum.conf import forum_settings
from the_tale.forum.prototypes import (ThreadPrototype,
                              SubCategoryPrototype,
                              CategoryPrototype,
                              ThreadReadInfoPrototype,
                              SubCategoryReadInfoPrototype,
                              PermissionPrototype,
                              SubscriptionPrototype)


class ThreadReadInfoPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(ThreadReadInfoPrototypeTests, self).setUp()
        create_test_map()

        register_user('user_1', 'user_1@test.com', '111111')
        register_user('user_2', 'user_2@test.com', '111111')

        self.account = AccountPrototype.get_by_nick('user_1')
        self.account_2 = AccountPrototype.get_by_nick('user_2')

        category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        subcategory = SubCategoryPrototype.create(category=category, caption='subcat-caption', order=0)

        self.thread = ThreadPrototype.create(subcategory, 'thread1-caption', self.account, 'thread-text')

    def test_remove_old_infos(self):
        read_info_1 = ThreadReadInfoPrototype.read_thread(self.thread, self.account)
        read_info_2 = ThreadReadInfoPrototype.read_thread(self.thread, self.account_2)

        removed_time = datetime.datetime.now() - datetime.timedelta(seconds=forum_settings.UNREAD_STATE_EXPIRE_TIME)
        ThreadReadInfoPrototype._model_class.objects.filter(id=read_info_2.id).update(read_at=removed_time)

        self.assertEqual(ThreadReadInfoPrototype._db_count(), 2)
        ThreadReadInfoPrototype.remove_old_infos()
        self.assertEqual(ThreadReadInfoPrototype._db_count(), 1)
        self.assertEqual(ThreadReadInfoPrototype._db_get_object(0).id, read_info_1.id)


    def test_read_thread__unexisted_info(self):
        self.assertEqual(ThreadReadInfoPrototype._db_count(), 0)
        read_info = ThreadReadInfoPrototype.read_thread(self.thread, self.account)
        self.assertEqual(ThreadReadInfoPrototype._db_count(), 1)
        self.assertEqual(read_info.thread_id, self.thread.id)
        self.assertEqual(read_info.account_id, self.account.id)
        self.assertTrue(read_info.read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))

    def test_read_thread__existed_info(self):
        self.assertEqual(ThreadReadInfoPrototype._db_count(), 0)
        read_info = ThreadReadInfoPrototype.read_thread(self.thread, self.account)
        read_info_2 = ThreadReadInfoPrototype.read_thread(self.thread, self.account)
        self.assertEqual(read_info.id, read_info_2.id)
        self.assertEqual(ThreadReadInfoPrototype._db_count(), 1)
        self.assertEqual(read_info.thread_id, self.thread.id)
        self.assertEqual(read_info.account_id, self.account.id)
        self.assertTrue(read_info.read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))


class SubCategoryReadInfoPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(SubCategoryReadInfoPrototypeTests, self).setUp()
        create_test_map()

        register_user('user_1', 'user_1@test.com', '111111')
        register_user('user_2', 'user_2@test.com', '111111')

        self.account = AccountPrototype.get_by_nick('user_1')
        self.account_2 = AccountPrototype.get_by_nick('user_2')

        category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = SubCategoryPrototype.create(category=category, caption='subcat-caption', order=0)

    def test_is_restricted_for__not_restricted(self):
        self.subcategory._model.restricted = False
        self.subcategory.save()
        self.assertFalse(self.subcategory.is_restricted_for(self.account))

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', lambda a: False)
    def test_is_restricted_for__not_authenticated(self):
        self.subcategory._model.restricted = True
        self.subcategory.save()
        self.assertTrue(self.subcategory.is_restricted_for(self.account))

    def test_is_restricted_for__has_permission(self):
        self.subcategory._model.restricted = True
        self.subcategory.save()
        PermissionPrototype.create(self.account, self.subcategory)
        self.assertFalse(self.subcategory.is_restricted_for(self.account))

    def test_is_restricted_for__no_permission(self):
        self.subcategory._model.restricted = True
        self.subcategory.save()
        PermissionPrototype.create(self.account_2, self.subcategory)
        self.assertTrue(self.subcategory.is_restricted_for(self.account))

    def test_create_when_created(self):
        read_info_1 = SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account)
        read_info_2 = SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account)

        self.assertEqual(read_info_1.id, read_info_2.id)

    def test_remove_old_infos(self):
        read_info_1 = SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account)
        read_info_2 = SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account_2)

        removed_time = datetime.datetime.now() - datetime.timedelta(seconds=forum_settings.UNREAD_STATE_EXPIRE_TIME)
        SubCategoryReadInfoPrototype._model_class.objects.filter(id=read_info_2.id).update(read_at=removed_time)

        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 2)
        SubCategoryReadInfoPrototype.remove_old_infos()
        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 1)
        self.assertEqual(SubCategoryReadInfoPrototype._db_get_object(0).id, read_info_1.id)


    def test_read_subcategory__unexisted_info(self):
        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 0)
        read_info = SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account)
        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 1)
        self.assertEqual(read_info.subcategory_id, self.subcategory.id)
        self.assertEqual(read_info.account_id, self.account.id)
        self.assertTrue(read_info.read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))
        self.assertTrue(read_info.all_read_at < datetime.datetime.now() - datetime.timedelta(seconds=1))

    def test_read_subcategory__existed_info(self):
        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 0)
        read_info = SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account)
        read_info_2 = SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account)
        self.assertEqual(read_info.id, read_info_2.id)
        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 1)
        self.assertEqual(read_info.subcategory_id, self.subcategory.id)
        self.assertEqual(read_info.account_id, self.account.id)
        self.assertTrue(read_info_2.read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))
        self.assertTrue(read_info_2.all_read_at < datetime.datetime.now() - datetime.timedelta(seconds=1))

    def test_read_all_in_subcategory__unexisted_info(self):
        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 0)
        read_info = SubCategoryReadInfoPrototype.read_all_in_subcategory(self.subcategory, self.account)
        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 1)
        self.assertEqual(read_info.subcategory_id, self.subcategory.id)
        self.assertEqual(read_info.account_id, self.account.id)
        self.assertTrue(read_info.read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))
        self.assertTrue(read_info.all_read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))

    def test_read_all_in_subcategory__existed_info(self):
        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 0)
        read_info = SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account)
        read_info_2 = SubCategoryReadInfoPrototype.read_all_in_subcategory(self.subcategory, self.account)
        self.assertEqual(read_info.id, read_info_2.id)
        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 1)
        self.assertEqual(read_info.subcategory_id, self.subcategory.id)
        self.assertEqual(read_info.account_id, self.account.id)
        self.assertTrue(read_info_2.read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))
        self.assertTrue(read_info_2.all_read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))


class SubscriptionPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(SubscriptionPrototypeTests, self).setUp()
        create_test_map()

        register_user('user_1', 'user_1@test.com', '111111')
        register_user('user_2', 'user_2@test.com', '111111')

        self.account = AccountPrototype.get_by_nick('user_1')
        self.account_2 = AccountPrototype.get_by_nick('user_2')

        self.category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory_1 = SubCategoryPrototype.create(category=self.category, caption='subcat-1-caption', order=0)
        self.subcategory_2 = SubCategoryPrototype.create(category=self.category, caption='subcat-2-caption', order=1)

        self.thread_1_1 = ThreadPrototype.create(self.subcategory_1, 'thread-1-1-caption', self.account, 'thread-1-1-text')
        self.thread_1_2 = ThreadPrototype.create(self.subcategory_1, 'thread-1-2-caption', self.account, 'thread-1-2-text')
        self.thread_1_3 = ThreadPrototype.create(self.subcategory_1, 'thread-1-3-caption', self.account_2, 'thread-1-3-text')
        self.thread_2_1 = ThreadPrototype.create(self.subcategory_2, 'thread-2-1-caption', self.account, 'thread-2-1-text')
        self.thread_2_2 = ThreadPrototype.create(self.subcategory_2, 'thread-2-2-caption', self.account, 'thread-2-2-text')


    def test_remove_all_in_subcategory(self):

        SubscriptionPrototype.create(account=self.account, subcategory=self.subcategory_1)
        subscr_2 = SubscriptionPrototype.create(account=self.account, subcategory=self.subcategory_2)

        SubscriptionPrototype.create(account=self.account, thread=self.thread_1_1)
        SubscriptionPrototype.create(account=self.account, thread=self.thread_1_2)
        subscr_5 = SubscriptionPrototype.create(account=self.account_2, thread=self.thread_1_2)
        subscr_6 = SubscriptionPrototype.create(account=self.account_2, thread=self.thread_1_3)

        subscr_7 = SubscriptionPrototype.create(account=self.account, thread=self.thread_2_1)

        self.assertEqual(SubscriptionPrototype._db_count(), 7)

        SubscriptionPrototype.remove_all_in_subcategory(account_id=self.account.id, subcategory_id=self.subcategory_1.id)

        self.assertEqual(SubscriptionPrototype._db_count(), 4)
        self.assertEqual(set(s.id for s in SubscriptionPrototype._db_all()),
                         set((subscr_2.id, subscr_5.id, subscr_6.id, subscr_7.id)))


class PermissionPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(PermissionPrototypeTests, self).setUp()
        create_test_map()

        register_user('user_1', 'user_1@test.com', '111111')

        self.account = AccountPrototype.get_by_nick('user_1')

        self.category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = SubCategoryPrototype.create(category=self.category, caption='subcat-caption', order=0)


    def test_remove(self):
        permission = PermissionPrototype.create(self.account, self.subcategory)

        with mock.patch('the_tale.forum.prototypes.SubscriptionPrototype.remove_all_in_subcategory') as remove_all_in_subcategory:
            permission.remove()

        self.assertEqual(remove_all_in_subcategory.call_count, 1)
        self.assertEqual(remove_all_in_subcategory.call_args, mock.call(account_id=self.account.id, subcategory_id=self.subcategory.id))
