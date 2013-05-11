# coding: utf-8

import datetime

from common.utils import testcase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map

from forum.conf import forum_settings
from forum.prototypes import ThreadPrototype, SubCategoryPrototype, CategoryPrototype, ThreadReadInfoPrototype, SubCategoryReadInfoPrototype


class ThreadReadInfoPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(ThreadReadInfoPrototypeTests, self).setUp()
        create_test_map()

        register_user('user_1', 'user_1@test.com', '111111')
        register_user('user_2', 'user_2@test.com', '111111')

        self.account = AccountPrototype.get_by_nick('user_1')
        self.account_2 = AccountPrototype.get_by_nick('user_2')

        category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        subcategory = SubCategoryPrototype.create(category=category, caption='subcat-caption', slug='subcat-slug', order=0)

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
        self.subcategory = SubCategoryPrototype.create(category=category, caption='subcat-caption', slug='subcat-slug', order=0)

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
