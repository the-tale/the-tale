# coding: utf-8
import mock

import datetime

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map
from the_tale.game.prototypes import TimePrototype

from the_tale.forum.conf import forum_settings
from the_tale.forum.prototypes import (ThreadPrototype,
                                       PostPrototype,
                                       SubCategoryPrototype,
                                       CategoryPrototype,
                                       ThreadReadInfoPrototype,
                                       SubCategoryReadInfoPrototype,
                                       PermissionPrototype,
                                       SubscriptionPrototype)
from the_tale.forum.relations import MARKUP_METHOD, POST_STATE


class SubcategoryPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(SubcategoryPrototypeTests, self).setUp()
        create_test_map()


    def test_subcategories_visible_to_account_with_permissions(self):
        register_user('test_user', 'test_user@test.com', '111111')
        register_user('granted_user', 'granted_user@test.com', '111111')
        register_user('wrong_user', 'wrong_user@test.com', '111111')

        granted_account = AccountPrototype.get_by_nick('granted_user')
        wrong_account = AccountPrototype.get_by_nick('wrong_user')

        category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        subcategory_1 = SubCategoryPrototype.create(category=category, caption='subcat-1-caption', order=2)

        SubCategoryPrototype.create(category=category, caption='subcat-2-caption', order=1, restricted=True)

        restricted_subcategory = SubCategoryPrototype.create(category=category, caption='subcat-restricted-caption', order=0, restricted=True)

        PermissionPrototype.create(granted_account, restricted_subcategory)

        self.assertEqual([s.id for s in SubCategoryPrototype.subcategories_visible_to_account(account=None)],
                         [subcategory_1.id])

        self.assertEqual([s.id for s in SubCategoryPrototype.subcategories_visible_to_account(account=granted_account)],
                         [restricted_subcategory.id, subcategory_1.id])

        self.assertEqual([s.id for s in SubCategoryPrototype.subcategories_visible_to_account(account=wrong_account)],
                         [subcategory_1.id])


class SubcategoryPrototypeUpdateTests(testcase.TestCase):

    def setUp(self):
        super(SubcategoryPrototypeUpdateTests, self).setUp()

        create_test_map()

        register_user('test_user', 'test_user@test.com', '111111')
        register_user('checked_user', 'granted_user@test.com', '111111')

        self.account = AccountPrototype.get_by_nick('test_user')
        self.checked_account = AccountPrototype.get_by_nick('checked_user')

        self.category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = SubCategoryPrototype.create(category=self.category, caption='subcat-caption', order=2)

        self.thread_1 = ThreadPrototype.create(self.subcategory, 'thread-1-caption', self.account, 'thread-1-text')
        self.thread_2 = ThreadPrototype.create(self.subcategory, 'thread-2-caption', self.account, 'thread-2-text')


    def test_automatic_update_on_post_creating(self):

        old_time = datetime.datetime.now()

        PostPrototype.create(thread=self.thread_2, author=self.checked_account, text='post-1-text')

        self.subcategory.reload()

        self.assertEqual(self.subcategory.threads_count, 2)
        self.assertEqual(self.subcategory.posts_count, 1)
        self.assertEqual(self.subcategory.last_poster.id, self.checked_account.id)
        self.assertEqual(self.subcategory.last_thread.id, self.thread_2.id)
        self.assertTrue(self.subcategory.updated_at > old_time)
        self.assertEqual(self.subcategory.last_thread_created_at, self.thread_2.created_at)

    def test_automatic_raw_update(self):
        old_time = datetime.datetime.now()

        PostPrototype._model_class.objects.create(thread=self.thread_1._model,
                                                  author=self.checked_account._model,
                                                  markup_method=MARKUP_METHOD.MARKDOWN,
                                                  technical=False,
                                                  text='post-2-text',
                                                  state=POST_STATE.DEFAULT)

        self.subcategory.reload()

        self.assertEqual(self.subcategory.posts_count, 0)
        self.assertEqual(self.subcategory.last_poster.id, self.account.id)
        self.assertEqual(self.subcategory.last_thread.id, self.thread_2.id)
        self.assertTrue(self.subcategory.updated_at < old_time)

        self.subcategory.update()
        self.subcategory.reload()

        self.assertEqual(self.subcategory.posts_count, 1)
        self.assertEqual(self.subcategory._model.last_poster_id, self.checked_account.id)
        self.assertEqual(self.subcategory._model.last_thread_id, self.thread_1.id)
        self.assertTrue(old_time < self.subcategory.updated_at)

    def test_automatic_update_on_post_deleting(self):

        old_time = datetime.datetime.now()

        self.test_automatic_update_on_post_creating()

        PostPrototype._db_get_object(2).delete(self.checked_account)

        self.subcategory.update()

        self.assertEqual(self.subcategory.posts_count, 1)
        self.assertEqual(self.subcategory._model.last_poster.id, self.account.id)
        self.assertEqual(self.subcategory._model.last_thread.id, self.thread_2.id)
        self.assertTrue(self.subcategory.updated_at < old_time)

        PostPrototype._db_get_object(1).delete(self.checked_account)

        self.subcategory.update()

        self.assertEqual(self.subcategory.posts_count, 1)
        self.assertEqual(self.subcategory._model.last_poster.id, self.account.id)
        self.assertEqual(self.subcategory._model.last_thread.id, self.thread_1.id)
        self.assertTrue(self.subcategory.updated_at < old_time)



class ThreadPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(ThreadPrototypeTests, self).setUp()
        create_test_map()

        register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_nick('test_user')

        self.category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = SubCategoryPrototype.create(category=self.category, caption='subcat-caption', order=0)

        self.thread = ThreadPrototype.create(self.subcategory, 'thread-caption', self.account, 'thread-text')

    def test_get_new_thread_delay__no_threads__new_account(self):
        register_user('new_test_user', 'new_test_user@test.com', '111111')
        new_account = AccountPrototype.get_by_nick('new_test_user')
        self.assertTrue(ThreadPrototype.get_new_thread_delay(new_account) > 0)

    def test_get_new_thread_delay__no_threads__old_account(self):
        register_user('new_test_user', 'new_test_user@test.com', '111111')
        new_account = AccountPrototype.get_by_nick('new_test_user')
        new_account._model.created_at = datetime.datetime.now() - datetime.timedelta(days=30)
        self.assertFalse(ThreadPrototype.get_new_thread_delay(new_account), 0)

    def test_get_new_thread_delay__has_old_thread(self):
        ThreadPrototype._db_all().update(created_at=datetime.datetime.now() - datetime.timedelta(days=30))
        self.assertEqual(ThreadPrototype.get_new_thread_delay(self.account), 0)

    def test_get_new_thread_delay__has_new_thread(self):
        self.assertTrue(ThreadPrototype.get_new_thread_delay(self.account) > 0)


    def test_last_forum_posts_with_permissions(self):

        register_user('granted_user', 'granted_user@test.com', '111111')
        register_user('wrong_user', 'wrong_user@test.com', '111111')


        granted_account = AccountPrototype.get_by_nick('granted_user')
        wrong_account = AccountPrototype.get_by_nick('wrong_user')

        restricted_subcategory = SubCategoryPrototype.create(category=self.category, caption='subcat2-caption', order=1, restricted=True)

        PermissionPrototype.create(granted_account, restricted_subcategory)

        restricted_thread = ThreadPrototype.create(restricted_subcategory, 'thread-restricted-caption', self.account, 'thread-text')

        self.assertEqual(set(t.id for t in ThreadPrototype.get_last_threads(account=None, limit=3)),
                         set([self.thread.id]))

        self.assertEqual(set(t.id for t in ThreadPrototype.get_last_threads(account=granted_account, limit=3)),
                         set([self.thread.id, restricted_thread.id]))

        self.assertEqual(set(t.id for t in ThreadPrototype.get_last_threads(account=wrong_account, limit=3)),
                         set([self.thread.id]))



    def test_update_subcategory_on_delete(self):
        with mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.update') as subcategory_update:
            self.thread.delete()

        self.assertEqual(subcategory_update.call_count, 1)

    def test_update_subcategory_on_create(self):
        with mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.update') as subcategory_update:
            ThreadPrototype.create(self.subcategory, 'thread-2-caption', self.account, 'thread-2-text')

        self.assertEqual(subcategory_update.call_count, 1)

    def test_post_created_at_turn(self):
        current_turn = TimePrototype.get_current_time()

        current_turn.increment_turn()
        current_turn.increment_turn()

        ThreadPrototype.create(self.subcategory, 'thread-2-caption', self.account, 'thread-2-text')

        self.assertEqual(PostPrototype._db_latest().created_at_turn, current_turn.turn_number)


class ThreadPrototypeUpdateTests(testcase.TestCase):

    def setUp(self):
        super(ThreadPrototypeUpdateTests, self).setUp()

        create_test_map()

        register_user('test_user', 'test_user@test.com', '111111')
        register_user('checked_user', 'granted_user@test.com', '111111')

        self.account = AccountPrototype.get_by_nick('test_user')
        self.checked_account = AccountPrototype.get_by_nick('checked_user')

        self.category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = SubCategoryPrototype.create(category=self.category, caption='subcat-caption', order=2)

        self.thread = ThreadPrototype.create(self.subcategory, 'thread-caption', self.account, 'thread-text')


    def test_automatic_update_on_post_creating(self):

        old_time = datetime.datetime.now()

        PostPrototype.create(thread=self.thread, author=self.checked_account, text='post-1-text')

        self.thread.reload()

        self.assertEqual(self.thread.posts_count, 1)
        self.assertEqual(self.thread.last_poster.id, self.checked_account.id)
        self.assertTrue(self.thread.updated_at > old_time)

    def test_automatic_raw_update(self):

        old_time = datetime.datetime.now()

        PostPrototype._model_class.objects.create(thread=self.thread._model,
                                                  author=self.checked_account._model,
                                                  markup_method=MARKUP_METHOD.MARKDOWN,
                                                  technical=False,
                                                  text='post-2-text',
                                                  state=POST_STATE.DEFAULT)

        self.thread.reload()

        self.assertEqual(self.thread.posts_count, 0)
        self.assertEqual(self.thread.last_poster.id, self.account.id)
        self.assertTrue(self.thread.updated_at < old_time)

        self.thread.update()
        self.thread.reload()

        self.assertEqual(self.thread.posts_count, 1)
        self.assertEqual(self.thread._model.last_poster.id, self.checked_account.id)
        self.assertTrue(old_time < self.thread.updated_at)

    def test_automatic_update_on_post_deleting(self):

        old_time = datetime.datetime.now()

        self.test_automatic_update_on_post_creating()

        PostPrototype._db_get_object(1).delete(self.checked_account)

        self.thread.update()

        self.assertEqual(self.thread.posts_count, 1)
        self.assertEqual(self.thread._model.last_poster.id, self.account.id)
        self.assertTrue(self.thread.updated_at < old_time)

    def test_subcategory_updated(self):
        with mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.update') as subcategory_update:
            self.thread.update()

        self.assertEqual(subcategory_update.call_count, 1)


    def test_2_subcategories_updated(self):
        subcategory_2 = SubCategoryPrototype.create(category=self.category, caption='subcat-2-caption', order=3)

        with mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.update') as subcategory_update:
            self.thread.update(new_subcategory_id=subcategory_2.id)

        self.assertEqual(subcategory_update.call_count, 2)



class PostPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(PostPrototypeTests, self).setUp()

        create_test_map()

        register_user('test_user', 'test_user@test.com', '111111')
        register_user('checked_user', 'granted_user@test.com', '111111')

        self.account = AccountPrototype.get_by_nick('test_user')
        self.checked_account = AccountPrototype.get_by_nick('checked_user')

        self.category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = SubCategoryPrototype.create(category=self.category, caption='subcat-caption', order=2)

        self.thread = ThreadPrototype.create(self.subcategory, 'thread-caption', self.account, 'thread-text')

    def test_get_new_post_delay__no_posts__new_account(self):
        register_user('new_test_user', 'new_test_user@test.com', '111111')
        new_account = AccountPrototype.get_by_nick('new_test_user')
        self.assertTrue(PostPrototype.get_new_post_delay(new_account) > 0)

    def test_get_new_post_delay__no_posts__old_account(self):
        register_user('new_test_user', 'new_test_user@test.com', '111111')
        new_account = AccountPrototype.get_by_nick('new_test_user')
        new_account._model.created_at = datetime.datetime.now() - datetime.timedelta(days=30)
        self.assertFalse(PostPrototype.get_new_post_delay(new_account), 0)

    def test_get_new_post_delay__has_old_post(self):
        PostPrototype.create(thread=self.thread, author=self.account, text='post-1-text')
        PostPrototype._db_all().update(created_at=datetime.datetime.now() - datetime.timedelta(days=30))
        self.assertEqual(PostPrototype.get_new_post_delay(self.account), 0)

    def test_get_new_post_delay__has_new_post(self):
        PostPrototype.create(thread=self.thread, author=self.account, text='post-1-text')
        self.assertTrue(PostPrototype.get_new_post_delay(self.account) > 0)

    def test_get_new_post_delay__more_then_one_post(self):
        PostPrototype.create(thread=self.thread, author=self.account, text='post-1-text')
        delay_1 = PostPrototype.get_new_post_delay(self.account)

        PostPrototype.create(thread=self.thread, author=self.account, text='post-1-text')

        delay_2 = PostPrototype.get_new_post_delay(self.account)

        self.assertTrue(delay_1 - delay_2 > 1)

    def test_get_new_post_delay__a_lot_of_posts(self):
        for i in xrange(100):
            PostPrototype.create(thread=self.thread, author=self.account, text='post-1-text')

        self.assertTrue(PostPrototype.get_new_post_delay(self.account) < forum_settings.POST_DELAY)

    def test_update_thread_on_delete(self):
        with mock.patch('the_tale.forum.prototypes.ThreadPrototype.update') as thread_update:
            PostPrototype._db_get_object(0).delete(self.checked_account)

        self.assertEqual(thread_update.call_count, 1)

    def test_created_at_turn(self):
        current_turn = TimePrototype.get_current_time()

        current_turn.increment_turn()
        current_turn.increment_turn()

        post = PostPrototype.create(thread=self.thread, author=self.account, text='post-1-text')

        self.assertEqual(post.created_at_turn, current_turn.turn_number)


    def test_update_thread_on_create(self):
        with mock.patch('the_tale.forum.prototypes.ThreadPrototype.update') as thread_update:
            PostPrototype.create(thread=self.thread, author=self.checked_account, text='post-1-text')

        self.assertEqual(thread_update.call_count, 1)


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
