# coding: utf-8
import datetime

import mock

from dext.utils.urls import url

from the_tale.common.utils import testcase

from the_tale.accounts.logic import login_page_url

from the_tale.game.logic import create_test_map

from the_tale.forum.models import Category, SubCategory, Thread, Post, Subscription
from the_tale.forum.prototypes import (ThreadPrototype,
                              PostPrototype,
                              ThreadReadInfoPrototype,
                              SubCategoryReadInfoPrototype)
from the_tale.forum.conf import forum_settings
from the_tale.forum.tests.helpers import ForumFixture


class BaseTestRequests(testcase.TestCase):

    def setUp(self):
        super(BaseTestRequests, self).setUp()
        create_test_map()

        self.fixture = ForumFixture()

        self.account = self.fixture.account_1
        self.account_2 = self.fixture.account_2

        self.request_login(self.account.email)

        # cat1
        # |-subcat1
        # | |-thread1
        # | | |-post1
        # | |-thread2
        # |-subcat2
        # cat2
        # | subcat3
        # | |- thread3
        # cat3

        self.cat1 = self.fixture.cat_1
        # to test, that subcat.id not correlate with order
        self.subcat2 = self.fixture.subcat_2
        self.subcat1 = self.fixture.subcat_1
        self.cat2 = self.fixture.cat_2
        self.subcat3 = self.fixture.subcat_3
        self.cat3 = self.fixture.cat_3

        self.thread1 = self.fixture.thread_1
        self.thread2 = self.fixture.thread_2
        self.thread3 = self.fixture.thread_3

        self.post1 = self.fixture.post_1


class ForumResourceReadAllTests(BaseTestRequests):

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(url('forum:read-all', self.subcat1.id)), 'common.login_required')
        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 0)

    def test_success(self):
        self.check_ajax_ok(self.client.post(url('forum:read-all', self.subcat1.id)))
        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 1)
        read_info = SubCategoryReadInfoPrototype._db_get_object(0)
        self.assertEqual(read_info.account_id, self.account.id)
        self.assertEqual(read_info.subcategory_id, self.subcat1.id)
        self.assertTrue(read_info.all_read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))


class TestRequests(BaseTestRequests):

    def test_initialization(self):
        self.assertEqual(Category.objects.all().count(), 4)
        self.assertEqual(SubCategory.objects.all().count(), 4)
        self.assertEqual(Thread.objects.all().count(), 3)
        self.assertEqual(Post.objects.all().count(), 4)

        self.assertEqual(SubCategory.objects.get(id=self.subcat1.id).posts_count, 1)
        self.assertEqual(Thread.objects.get(id=self.thread1.id).posts_count, 1)

    def test_index(self):
        texts = ['cat1-caption', 'cat2-caption', 'cat3-caption',
                 'subcat1-caption', 'subcat2-caption', 'subcat3-caption', self.fixture.clan_1.abbr]
        self.check_html_ok(self.request_html(url('forum:')), texts=texts)
        self.request_logout()
        self.check_html_ok(self.request_html(url('forum:')), texts=texts)


class TestSubcategoryRequests(BaseTestRequests):

    def test_subcategory__unlogined(self):
        texts = ['cat1-caption', 'subcat1-caption', 'thread1-caption', 'thread2-caption', self.fixture.clan_1.abbr]
        self.request_logout()
        self.check_html_ok(self.request_html(url('forum:subcategories:show', self.subcat1.id)), texts=texts)

        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 0)

    def test_subcategory(self):
        self.request_logout()
        self.request_login(self.account_2.email)
        texts = ['cat1-caption', 'subcat1-caption', 'thread1-caption', 'thread2-caption', 'pgf-new-thread-marker', self.fixture.clan_1.abbr]
        self.check_html_ok(self.request_html(url('forum:subcategories:show', self.subcat1.id)), texts=texts)

        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 1)
        read_info = SubCategoryReadInfoPrototype._db_get_object(0)
        self.assertEqual(read_info.account_id, self.account_2.id)
        self.assertEqual(read_info.subcategory_id, self.subcat1.id)

        self.check_html_ok(self.request_html(url('forum:subcategories:show', self.subcat1.id)), texts=[('pgf-new-thread-marker', 0)])

    @mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.is_restricted_for', lambda proto, account: True)
    def test_restricted(self):
        self.check_html_ok(self.request_html(url('forum:subcategories:show', self.subcat1.id)), texts=['forum.subcategory_access_restricted'])

    def test_subcategory_not_found(self):
        self.check_html_ok(self.request_html(url('forum:subcategories:show', 666)), texts=[('forum.subcategory.not_found', 1)], status_code=404)


class TestNewThreadRequests(BaseTestRequests):

    def test_new_thread(self):
        texts = ['cat1-caption', 'subcat1-caption']
        self.check_html_ok(self.request_html(url('forum:subcategories:new-thread', self.subcat1.id)), texts=texts)

    def test_new_thread_unlogined(self):
        self.request_logout()
        request_url = url('forum:subcategories:new-thread', self.subcat1.id)
        self.check_redirect(request_url, login_page_url(request_url))

    def test_new_thread_fast(self):
        self.account.is_fast = True
        self.account.save()
        self.check_html_ok(self.request_html(url('forum:subcategories:new-thread', self.subcat1.id)), texts=['pgf-error-common.fast_account'])

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_new_thread_banned(self):
        self.check_html_ok(self.request_html(url('forum:subcategories:new-thread', self.subcat1.id)), texts=['pgf-error-common.ban_forum'])

    @mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.is_restricted_for', lambda proto, account: True)
    def test_restricted(self):
        self.check_html_ok(self.request_html(url('forum:subcategories:new-thread', self.subcat1.id)), texts=['forum.subcategory_access_restricted'])


class TestCreateThreadRequests(BaseTestRequests):

    def test_create_thread_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(url('forum:subcategories:create-thread',  self.subcat1.id)),
                              code='common.login_required')

    def test_create_thread_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(url('forum:subcategories:create-thread',  self.subcat1.id)),
                              code='common.fast_account')

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_create_thread_banned(self):
        self.check_ajax_error(self.client.post(url('forum:subcategories:create-thread',  self.subcat1.id)),
                              code='common.ban_forum')

    def test_create_thread_closed_subcategory(self):
        self.check_ajax_error(self.client.post(url('forum:subcategories:create-thread',  self.subcat2.id)),
                              code='forum.create_thread.no_permissions')

    def test_create_thread_form_errors(self):
        self.check_ajax_error(self.client.post(url('forum:subcategories:create-thread',  self.subcat1.id)),
                              code='forum.create_thread.form_errors')

    def test_create_thread_form_errors__empty_caption(self):
        self.check_ajax_error(self.client.post(url('forum:subcategories:create-thread',  self.subcat1.id), {'caption': '', 'text': 'thread4-text'}),
                              code='forum.create_thread.form_errors')

    def test_create_thread_form_errors__empty_body(self):
        self.check_ajax_error(self.client.post(url('forum:subcategories:create-thread',  self.subcat1.id), {'caption': 'thread4-caption', 'text': ''}),
                              code='forum.create_thread.form_errors')

    def test_create_thread_success(self):
        response = self.client.post(url('forum:subcategories:create-thread',  self.subcat1.id), {'caption': 'thread4-caption', 'text': 'thread4-text'})

        thread = Thread.objects.all().order_by('-created_at')[0]

        self.check_ajax_ok(response, {'thread_id': thread.id,
                                      'thread_url': url('forum:threads:show', thread.id)})

        self.assertEqual(thread.posts_count, 0)
        self.assertEqual(thread.caption, 'thread4-caption')
        self.assertEqual(thread.author.id, self.account.id)

        post = Post.objects.filter(thread=thread)[0]
        self.assertEqual(post.text, 'thread4-text')
        self.assertEqual(post.author.id, self.account.id)

        self.assertEqual(Thread.objects.all().count(), 4)
        self.assertEqual(Post.objects.all().count(), 5)

        self.assertEqual(SubCategory.objects.get(id=self.subcat1.id).posts_count, 1)

    @mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.is_restricted_for', lambda proto, account: True)
    def test_restricted(self):
        self.check_ajax_error(self.client.post(url('forum:subcategories:create-thread',  self.subcat1.id)), 'forum.subcategory_access_restricted')


class TestIndexThreadsRequests(BaseTestRequests):

    def setUp(self):
        super(TestIndexThreadsRequests, self).setUp()
        self.index_url = url('forum:threads:')

    def test_show_all(self):
        self.check_html_ok(self.request_html(self.index_url), texts=[t.caption for t in ThreadPrototype._db_all()])

    def test_no_restricted_threads(self):
        self.subcat3._model.restricted = True
        self.subcat3.save()

        self.check_html_ok(self.request_html(self.index_url), texts=[self.thread1.caption, self.thread2.caption, (self.thread3.caption, 0)])


class TestShowThreadRequests(BaseTestRequests):

    def test_get_thread_unlogined(self):
        self.request_logout()
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread1.id)), texts=(('pgf-new-post-form', 0),
                                                                                                 self.fixture.clan_1.abbr))
        self.assertEqual(ThreadReadInfoPrototype._db_count(), 0)

    def test_get_thread_not_found(self):
        self.check_html_ok(self.request_html(url('forum:threads:show', 666)), texts=(('forum.thread.not_found', 1),), status_code=404)

    def test_get_thread_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread1.id)), texts=(('pgf-new-post-form', 0),))

    def test_get_thread(self):
        self.assertEqual(ThreadReadInfoPrototype._db_count(), 0)
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread1.id)), texts=('pgf-new-post-form',))
        self.assertEqual(ThreadReadInfoPrototype._db_count(), 1)

    def test_get_thread_wrong_page(self):
        response = self.request_html(url('forum:threads:show', self.thread1.id)+'?page=2')
        self.assertRedirects(response, url('forum:threads:show', self.thread1.id)+'?page=1', status_code=302, target_status_code=200)

    def test_get_thread_with_pagination(self):

        texts = []

        for i in xrange(forum_settings.POSTS_ON_PAGE-1):
            text = 'subcat3-post%d-text' % i
            PostPrototype.create(self.thread3, self.account, text)
            texts.append(text)

        response = self.request_html(url('forum:threads:show', self.thread3.id)+'?page=2')
        self.assertRedirects(response, url('forum:threads:show', self.thread3.id)+'?page=1', status_code=302, target_status_code=200)

        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread3.id)), texts=texts)

        text = 'subcat3-post%d-text' % (forum_settings.POSTS_ON_PAGE)
        PostPrototype.create(self.thread3, self.account, text)
        texts.append((text, 0))

        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread3.id)+'?page=1'), texts=texts)
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread3.id)+'?page=2'), texts=[text])

    def test_posts_count(self):
        for i in xrange(4):
            PostPrototype.create(self.thread1, self.account, 'subcat1-thread1-post%d-text' % i)

        for i in xrange(7):
            PostPrototype.create(self.thread2, self.account, 'subcat1-thread2-post%d-text' % i)

        # first post in thread does not count
        self.assertEqual(SubCategory.objects.get(id=self.subcat1.id).posts_count, 12)
        self.assertEqual(Thread.objects.get(id=self.thread1.id).posts_count, 5)
        self.assertEqual(Thread.objects.get(id=self.thread2.id).posts_count, 7)

    @mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.is_restricted_for', lambda proto, account: True)
    def test_restricted(self):
        self.check_html_ok(self.request_html(url('forum:threads:show', self.thread1.id)), texts=('forum.subcategory_access_restricted',))


class TestCreatePostRequests(BaseTestRequests):

    def test_create_post_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(url('forum:threads:create-post', self.thread3.id)),
                              code='common.login_required')

    def test_create_post_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(url('forum:threads:create-post', self.thread3.id)),
                              code='common.fast_account')

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_create_post_banned(self):
        self.check_ajax_error(self.client.post(url('forum:threads:create-post', self.thread3.id)),
                              code='common.ban_forum')

    def test_create_post_form_errors(self):
        self.check_ajax_error(self.client.post(url('forum:threads:create-post', self.thread3.id)),
                              code='forum.create_post.form_errors')

    def test_create_post_form_errors__empty_post(self):
        self.check_ajax_error(self.client.post(url('forum:threads:create-post', self.thread3.id), {'text': ''}),
                              code='forum.create_post.form_errors')

    def test_create_post_success(self):
        self.check_ajax_ok(self.client.post(url('forum:threads:create-post', self.thread3.id), {'text': 'thread3-test-post'}),
                           data={'thread_url': url('forum:threads:show', self.thread3.id) + '?page=1'})
        self.assertEqual(Post.objects.all().count(), 5)

    def test_create_post_thread_not_found(self):
        self.check_ajax_error(self.client.post(url('forum:threads:create-post', 666), {'text': 'thread3-test-post'}),
                              'forum.thread.not_found')

    @mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.is_restricted_for', lambda proto, account: True)
    def test_restricted(self):
        self.check_ajax_error(self.client.post(url('forum:threads:create-post', self.thread3.id), {'text': 'thread3-test-post'}),
                              'forum.subcategory_access_restricted')



class TestFeedRequests(BaseTestRequests):

    def test_feed_page(self):

        self.thread1._model.created_at -= datetime.timedelta(seconds=forum_settings.FEED_ITEMS_DELAY+1)
        self.thread1.save()

        self.thread3._model.created_at -= datetime.timedelta(seconds=forum_settings.FEED_ITEMS_DELAY+1)
        self.thread3.save()

        PostPrototype.create(self.thread1, self.account, 'post2-text')
        PostPrototype.create(self.thread1, self.account, 'post3-text')
        PostPrototype.create(self.thread2, self.account, 'post4-text')
        PostPrototype.create(self.thread2, self.account, 'post5-text')
        PostPrototype.create(self.thread3, self.account, 'post6-text')

        # restricted
        self.subcat2._model.restricted = True
        self.subcat2.save()

        thread2_2 = ThreadPrototype.create(self.subcat2, 'thread2_2-caption', self.account, 'thread2_2-text')

        PostPrototype.create(thread2_2, self.account, 'post7-text')
        PostPrototype.create(thread2_2, self.account, 'post8-text')

        texts = [('thread1-caption', 1),
                 ('thread1-text', 1),

                 ('thread2-caption', 0), # not pass throught time limit
                 ('thread2-text', 0),

                 ('thread3-caption', 1),
                 ('thread3-text', 1),

                 ('thread2_2-caption', 0),
                 ('thread2_2-text', 0)]

        texts.extend([('post%d-text' % i, 0) for i in xrange(0, 9)])

        self.check_html_ok(self.request_html(url('forum:feed')), texts=texts, content_type='application/atom+xml')


class ThreadSubscribeTests(BaseTestRequests):

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(url('forum:threads:subscribe', self.thread1.id)),
                              'common.login_required')

    def test_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(url('forum:threads:subscribe', self.thread1.id)),
                              'common.fast_account')

    def test_create_for_thread(self):
        self.assertEqual(Subscription.objects.all().count(), 0)
        self.check_ajax_ok(self.client.post(url('forum:threads:subscribe', self.thread1.id)))
        self.assertEqual(Subscription.objects.all().count(), 1)

    def test_create_when_exists(self):
        self.assertEqual(Subscription.objects.all().count(), 0)
        self.check_ajax_ok(self.client.post(url('forum:threads:subscribe', self.thread1.id)))
        self.check_ajax_ok(self.client.post(url('forum:threads:subscribe', self.thread1.id)))
        self.assertEqual(Subscription.objects.all().count(), 1)

    @mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.is_restricted_for', lambda proto, account: True)
    def test_restricted(self):
        self.check_ajax_error(self.client.post(url('forum:threads:subscribe', self.thread1.id)),
                              'forum.subcategory_access_restricted')

class SubcategorySubscribeTests(BaseTestRequests):

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(url('forum:subcategories:subscribe', self.subcat2.id)), 'common.login_required')

    def test_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(url('forum:subcategories:subscribe', self.subcat2.id)), 'common.fast_account')

    def test_create_for_subcategory(self):
        self.assertEqual(Subscription.objects.all().count(), 0)
        self.check_ajax_ok(self.client.post(url('forum:subcategories:subscribe', self.subcat2.id)))
        self.assertEqual(Subscription.objects.all().count(), 1)

    def test_create_when_exists(self):
        self.assertEqual(Subscription.objects.all().count(), 0)
        self.check_ajax_ok(self.client.post(url('forum:subcategories:subscribe', self.subcat2.id)))
        self.check_ajax_ok(self.client.post(url('forum:subcategories:subscribe', self.subcat2.id)))
        self.assertEqual(Subscription.objects.all().count(), 1)

    @mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.is_restricted_for', lambda proto, account: True)
    def test_restricted(self):
        self.check_ajax_error(self.client.post(url('forum:subcategories:subscribe', self.subcat2.id)),
                              'forum.subcategory_access_restricted')


class ThreadUnsubscribeTests(BaseTestRequests):

    def setUp(self):
        super(ThreadUnsubscribeTests, self).setUp()
        self.check_ajax_ok(self.client.post(url('forum:threads:subscribe', self.thread1.id)))

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(url('forum:threads:unsubscribe', self.thread1.id)),
                              'common.login_required')

    def test_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(url('forum:threads:unsubscribe', self.thread1.id)),
                              'common.fast_account')

    def test_remove_for_thread(self):
        self.assertEqual(Subscription.objects.all().count(), 1)
        self.check_ajax_ok(self.client.post(url('forum:threads:unsubscribe', self.thread1.id)))
        self.assertEqual(Subscription.objects.all().count(), 0)

    def test_remove_when_not_exists(self):
        self.assertEqual(Subscription.objects.all().count(), 1)
        self.check_ajax_ok(self.client.post(url('forum:threads:unsubscribe', self.thread1.id)))
        self.check_ajax_ok(self.client.post(url('forum:threads:unsubscribe', self.thread1.id)))
        self.assertEqual(Subscription.objects.all().count(), 0)

    @mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.is_restricted_for', lambda proto, account: True)
    def test_restricted(self):
        self.check_ajax_error(self.client.post(url('forum:threads:unsubscribe', self.thread1.id)),
                              'forum.subcategory_access_restricted')


class SubcategoryUnsubscribeTests(BaseTestRequests):

    def setUp(self):
        super(SubcategoryUnsubscribeTests, self).setUp()
        self.check_ajax_ok(self.client.post(url('forum:subcategories:subscribe', self.subcat2.id)))

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(url('forum:subcategories:unsubscribe', self.subcat2.id)),
                              'common.login_required')

    def test_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(url('forum:subcategories:unsubscribe', self.subcat2.id)),
                              'common.fast_account')

    def test_remove_for_subcategory(self):
        self.assertEqual(Subscription.objects.all().count(), 1)
        self.check_ajax_ok(self.client.post(url('forum:subcategories:unsubscribe', self.subcat2.id)))
        self.assertEqual(Subscription.objects.all().count(), 0)

    def test_remove_when_not_exists(self):
        self.assertEqual(Subscription.objects.all().count(), 1)
        self.check_ajax_ok(self.client.post(url('forum:subcategories:unsubscribe', self.subcat2.id)))
        self.check_ajax_ok(self.client.post(url('forum:subcategories:unsubscribe', self.subcat2.id)))
        self.assertEqual(Subscription.objects.all().count(), 0)

    @mock.patch('the_tale.forum.prototypes.SubCategoryPrototype.is_restricted_for', lambda proto, account: True)
    def test_restricted(self):
        self.check_ajax_error(self.client.post(url('forum:subcategories:unsubscribe', self.subcat2.id)),
                              'forum.subcategory_access_restricted')



class SubscriptionsTests(BaseTestRequests):

    def setUp(self):
        super(SubscriptionsTests, self).setUp()

    def test_login_required(self):
        self.request_logout()
        request_url = url('forum:subscriptions:')
        self.check_redirect(request_url, login_page_url(request_url))

    def test_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(url('forum:subscriptions:')),
                              'common.fast_account')

    def test_empty(self):
        texts = [('thread1-caption', 0),
                 ('thread2-caption', 0),
                 ('thread3-caption', 0),
                 ('subcat1-caption', 0),
                 ('subcat2-caption', 0),
                 ('pgf-no-thread-subscriptions-message', 1),
                 ('pgf-no-subcategory-subscriptions-message', 1)]
        self.check_html_ok(self.request_html(url('forum:subscriptions:')), texts=texts)

    def test_subscriptions(self):
        self.check_ajax_ok(self.client.post(url('forum:threads:subscribe', self.thread1.id)))
        self.check_ajax_ok(self.client.post(url('forum:threads:subscribe', self.thread3.id)))
        self.check_ajax_ok(self.client.post(url('forum:subcategories:subscribe', self.subcat2.id)))

        texts = [('thread1-caption', 1),
                 ('thread2-caption', 0),
                 ('thread3-caption', 1),
                 ('subcat1-caption', 0),
                 ('subcat2-caption', 1),
                 ('pgf-no-thread-subscriptions-message', 0),
                 ('pgf-no-subcategory-subscriptions-message', 0)]
        self.check_html_ok(self.request_html(url('forum:subscriptions:')), texts=texts)
