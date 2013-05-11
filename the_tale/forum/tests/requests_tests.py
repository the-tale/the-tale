# coding: utf-8
import datetime

from django.test import client
from django.core.urlresolvers import reverse

from common.utils import testcase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, login_url
from game.logic import create_test_map

from forum.models import Category, SubCategory, Thread, Post, Subscription
from forum.prototypes import ThreadPrototype, PostPrototype, SubCategoryPrototype, CategoryPrototype, ThreadReadInfoPrototype, SubCategoryReadInfoPrototype
from forum.conf import forum_settings


class BaseTestRequests(testcase.TestCase):

    def setUp(self):
        super(BaseTestRequests, self).setUp()
        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')
        register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.account = AccountPrototype.get_by_nick('test_user')
        self.account_2 = AccountPrototype.get_by_nick('test_user_2')

        self.client = client.Client()
        self.request_login('test_user@test.com')

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

        self.cat1 = CategoryPrototype.create(caption='cat1-caption', slug='cat1-slug', order=0)
        # to test, that subcat.id not correlate with order
        self.subcat2 = SubCategoryPrototype.create(category=self.cat1, caption='subcat2-caption', slug='subcat2-slug', order=1, closed=True)
        self.subcat1 = SubCategoryPrototype.create(category=self.cat1, caption='subcat1-caption', slug='subcat1-slug', order=0)
        self.cat2 = CategoryPrototype.create(caption='cat2-caption', slug='cat2-slug', order=0)
        self.subcat3 = SubCategoryPrototype.create(category=self.cat2, caption='subcat3-caption', slug='subcat3-slug', order=0)
        self.cat3 = CategoryPrototype.create(caption='cat3-caption', slug='cat3-slug', order=0)

        self.thread1 = ThreadPrototype.create(self.subcat1, 'thread1-caption', self.account, 'thread1-text')
        self.thread2 = ThreadPrototype.create(self.subcat1, 'thread2-caption', self.account, 'thread2-text')
        self.thread3 = ThreadPrototype.create(self.subcat3, 'thread3-caption', self.account, 'thread3-text')

        self.post1 = PostPrototype.create(self.thread1, self.account, 'post1-text')


class ForumResourceReadAllTests(BaseTestRequests):

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('forum:read-all', args=['subcat1-slug'])), 'common.login_required')
        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 0)

    def test_success(self):
        self.check_ajax_ok(self.client.post(reverse('forum:read-all', args=['subcat1-slug'])))
        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 1)
        read_info = SubCategoryReadInfoPrototype._db_get_object(0)
        self.assertEqual(read_info.account_id, self.account.id)
        self.assertEqual(read_info.subcategory_id, self.subcat1.id)
        self.assertTrue(read_info.all_read_at > datetime.datetime.now() - datetime.timedelta(seconds=1))


class TestRequests(BaseTestRequests):

    def test_initialization(self):
        self.assertEqual(Category.objects.all().count(), 3)
        self.assertEqual(SubCategory.objects.all().count(), 3)
        self.assertEqual(Thread.objects.all().count(), 3)
        self.assertEqual(Post.objects.all().count(), 4)

        self.assertEqual(SubCategory.objects.get(id=self.subcat1.id).posts_count, 1)
        self.assertEqual(Thread.objects.get(id=self.thread1.id).posts_count, 1)

    def test_index(self):
        texts = ['cat1-caption', 'cat1-slug', 'cat2-caption', 'cat2-slug', 'cat3-caption', 'cat3-slug',
                 'subcat1-caption', 'subcat1-slug', 'subcat2-caption', 'subcat2-slug', 'subcat3-caption', 'subcat3-slug',]
        self.check_html_ok(self.client.get(reverse('forum:')), texts=texts)
        self.request_logout()
        self.check_html_ok(self.client.get(reverse('forum:')), texts=texts)

    def test_subcategory__unlogined(self):
        texts=['cat1-caption', 'subcat1-caption', 'thread1-caption', 'thread2-caption']
        self.request_logout()
        self.check_html_ok(self.client.get(reverse('forum:subcategory', args=['subcat1-slug'])), texts=texts)

        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 0)


    def test_subcategory(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        texts=['cat1-caption', 'subcat1-caption', 'thread1-caption', 'thread2-caption', 'pgf-new-thread-marker']
        self.check_html_ok(self.client.get(reverse('forum:subcategory', args=['subcat1-slug'])), texts=texts)

        self.assertEqual(SubCategoryReadInfoPrototype._db_count(), 1)
        read_info = SubCategoryReadInfoPrototype._db_get_object(0)
        self.assertEqual(read_info.account_id, self.account_2.id)
        self.assertEqual(read_info.subcategory_id, self.subcat1.id)

        self.check_html_ok(self.client.get(reverse('forum:subcategory', args=['subcat1-slug'])), texts=[('pgf-new-thread-marker', 0)])

    def test_subcategory_not_found(self):
        self.check_html_ok(self.client.get(reverse('forum:subcategory', args=['subcatXXX-slug'])), texts=[('forum.subcategory.not_found', 1)], status_code=404)

    def test_new_thread(self):
        texts=['cat1-caption', 'subcat1-caption']
        self.check_html_ok(self.client.get(reverse('forum:threads:new') + ('?subcategory=%s' % self.subcat1.slug)), texts=texts)

    def test_new_thread_unlogined(self):
        self.request_logout()
        request_url = reverse('forum:threads:new') + ('?subcategory=%s' % self.subcat1.slug)
        self.assertRedirects(self.client.get(request_url), login_url(request_url), status_code=302, target_status_code=200)

    def test_new_thread_fast(self):
        self.account.is_fast = True
        self.account.save()
        self.check_html_ok(self.client.get(reverse('forum:threads:new') + ('?subcategory=%s' % self.subcat1.slug)), texts=['pgf-error-common.fast_account'])

    def test_create_thread_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('forum:threads:create') + ('?subcategory=%s' % self.subcat1.slug)),
                              code='common.login_required')

    def test_create_thread_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(reverse('forum:threads:create') + ('?subcategory=%s' % self.subcat1.slug)),
                              code='common.fast_account')

    def test_create_thread_closed_subcategory(self):
        self.check_ajax_error(self.client.post(reverse('forum:threads:create') + ('?subcategory=%s' % self.subcat2.slug)),
                              code='forum.create_thread.no_permissions')

    def test_create_thread_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('forum:threads:create') + ('?subcategory=%s' % self.subcat1.slug)),
                              code='forum.create_thread.form_errors')

    def test_create_thread_success(self):
        response = self.client.post(reverse('forum:threads:create') + ('?subcategory=%s' % self.subcat1.slug), {'caption': 'thread4-caption', 'text': 'thread4-text'})

        thread = Thread.objects.all().order_by('-created_at')[0]

        self.check_ajax_ok(response, {'thread_id': thread.id,
                                      'thread_url': reverse('forum:threads:show', args=[thread.id])})

        self.assertEqual(thread.posts_count, 0)
        self.assertEqual(thread.caption, 'thread4-caption')
        self.assertEqual(thread.author.id, self.account.id)

        post = Post.objects.filter(thread=thread)[0]
        self.assertEqual(post.text, 'thread4-text')
        self.assertEqual(post.author.id, self.account.id)

        self.assertEqual(Thread.objects.all().count(), 4)
        self.assertEqual(Post.objects.all().count(), 5)

        self.assertEqual(SubCategory.objects.get(id=self.subcat1.id).posts_count, 1)

    def test_get_thread_unlogined(self):
        self.request_logout()
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread1.id])), texts=(('pgf-new-post-form', 0),))
        self.assertEqual(ThreadReadInfoPrototype._db_count(), 0)

    def test_get_thread_not_found(self):
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[666])), texts=(('forum.thread.not_found', 1),), status_code=404)

    def test_get_thread_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread1.id])), texts=(('pgf-new-post-form', 0),))

    def test_get_thread(self):
        self.assertEqual(ThreadReadInfoPrototype._db_count(), 0)
        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread1.id])), texts=('pgf-new-post-form',))
        self.assertEqual(ThreadReadInfoPrototype._db_count(), 1)

    def test_get_thread_wrong_page(self):
        response = self.client.get(reverse('forum:threads:show', args=[self.thread1.id])+'?page=2')
        self.assertRedirects(response, reverse('forum:threads:show', args=[self.thread1.id])+'?page=1', status_code=302, target_status_code=200)

    def test_get_thread_with_pagination(self):

        texts = []

        for i in xrange(forum_settings.POSTS_ON_PAGE-1):
            text = 'subcat3-post%d-text' % i
            PostPrototype.create(self.thread3, self.account, text)
            texts.append(text)

        response = self.client.get(reverse('forum:threads:show', args=[self.thread3.id])+'?page=2')
        self.assertRedirects(response, reverse('forum:threads:show', args=[self.thread3.id])+'?page=1', status_code=302, target_status_code=200)

        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread3.id])), texts=texts)

        ++i
        text = 'subcat3-post%d-text' % i
        PostPrototype.create(self.thread3, self.account, text)
        texts.append(text)

        self.check_html_ok(self.client.get(reverse('forum:threads:show', args=[self.thread3.id])+'?page=1', texts=texts))
        response = self.client.get(reverse('forum:threads:show', args=[self.thread3.id])+'?page=2', texts=[text])

    def test_posts_count(self):
        for i in xrange(4):
            PostPrototype.create(self.thread1, self.account, 'subcat1-thread1-post%d-text' % i)

        for i in xrange(7):
            PostPrototype.create(self.thread2, self.account, 'subcat1-thread2-post%d-text' % i)

        # first post in thread does not count
        self.assertEqual(SubCategory.objects.get(id=self.subcat1.id).posts_count, 12)
        self.assertEqual(Thread.objects.get(id=self.thread1.id).posts_count, 5)
        self.assertEqual(Thread.objects.get(id=self.thread2.id).posts_count, 7)

    def test_create_post_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('forum:posts:create') + ('?thread=%d' % self.thread3.id)),
                              code='common.login_required')

    def test_create_post_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(reverse('forum:posts:create') + ('?thread=%d' % self.thread3.id)),
                              code='common.fast_account')

    def test_create_post_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('forum:posts:create') + ('?thread=%d' % self.thread3.id)),
                              code='forum.create_post.form_errors')

    def test_create_post_success(self):
        self.check_ajax_ok(self.client.post(reverse('forum:posts:create') + ('?thread=%d' % self.thread3.id), {'text': 'thread3-test-post'}),
                           data={'thread_url': reverse('forum:threads:show', args=[self.thread3.id]) + '?page=1'})
        self.assertEqual(Post.objects.all().count(), 5)

    def test_create_post_thread_not_found(self):
        self.check_ajax_error(self.client.post(reverse('forum:posts:create') + ('?thread=666'), {'text': 'thread3-test-post'}),
                              'forum.posts.create.thread.not_found')

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

        texts = [('thread1-caption', 1),
                 ('thread1-text', 1),

                 ('thread2-caption', 0), # not pass throught time limit
                 ('thread2-text', 0),

                 ('thread3-caption', 1),
                 ('thread3-text', 1), ]

        texts.extend([('post%d-text' % i, 0) for i in xrange(0, 6)])

        self.check_html_ok(self.client.get(reverse('forum:feed')), texts=texts, content_type='application/atom+xml')


class ThreadSubscribeTests(BaseTestRequests):

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('forum:subscriptions:subscribe')+('?thread=%d' % self.thread1.id)),
                              'common.login_required')

    def test_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(reverse('forum:subscriptions:subscribe')+('?thread=%d' % self.thread1.id)),
                              'common.fast_account')

    def test_create_for_thread(self):
        self.assertEqual(Subscription.objects.all().count(), 0)
        self.check_ajax_ok(self.client.post(reverse('forum:subscriptions:subscribe')+('?thread=%d' % self.thread1.id)))
        self.assertEqual(Subscription.objects.all().count(), 1)

    def test_create_for_subcategory(self):
        self.assertEqual(Subscription.objects.all().count(), 0)
        self.check_ajax_ok(self.client.post(reverse('forum:subscriptions:subscribe')+('?subcategory=%d' % self.subcat2.id)))
        self.assertEqual(Subscription.objects.all().count(), 1)

    def test_create_when_exists(self):
        self.assertEqual(Subscription.objects.all().count(), 0)
        self.check_ajax_ok(self.client.post(reverse('forum:subscriptions:subscribe')+('?thread=%d' % self.thread1.id)))
        self.check_ajax_ok(self.client.post(reverse('forum:subscriptions:subscribe')+('?thread=%d' % self.thread1.id)))
        self.assertEqual(Subscription.objects.all().count(), 1)


class ThreadUnsubscribeTests(BaseTestRequests):

    def setUp(self):
        super(ThreadUnsubscribeTests, self).setUp()
        self.check_ajax_ok(self.client.post(reverse('forum:subscriptions:subscribe')+('?thread=%d' % self.thread1.id)))
        self.check_ajax_ok(self.client.post(reverse('forum:subscriptions:subscribe')+('?subcategory=%d' % self.subcat2.id)))

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('forum:subscriptions:unsubscribe')+('?thread=%d' % self.thread1.id)),
                              'common.login_required')

    def test_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(reverse('forum:subscriptions:unsubscribe')+('?thread=%d' % self.thread1.id)),
                              'common.fast_account')

    def test_remove_for_thread(self):
        self.assertEqual(Subscription.objects.all().count(), 2)
        self.check_ajax_ok(self.client.post(reverse('forum:subscriptions:unsubscribe')+('?thread=%d' % self.thread1.id)))
        self.assertEqual(Subscription.objects.all().count(), 1)

    def test_remove_for_subcategory(self):
        self.assertEqual(Subscription.objects.all().count(), 2)
        self.check_ajax_ok(self.client.post(reverse('forum:subscriptions:unsubscribe')+('?subcategory=%d' % self.subcat2.id)))
        self.assertEqual(Subscription.objects.all().count(), 1)

    def test_remove_when_not_exists(self):
        self.assertEqual(Subscription.objects.all().count(), 2)
        self.check_ajax_ok(self.client.post(reverse('forum:subscriptions:unsubscribe')+('?thread=%d' % self.thread1.id)))
        self.check_ajax_ok(self.client.post(reverse('forum:subscriptions:unsubscribe')+('?thread=%d' % self.thread1.id)))
        self.assertEqual(Subscription.objects.all().count(), 1)


class SubscriptionsTests(BaseTestRequests):

    def setUp(self):
        super(SubscriptionsTests, self).setUp()

    def test_login_required(self):
        self.request_logout()
        url = reverse('forum:subscriptions:')
        self.check_redirect(url, login_url(url))

    def test_fast_account(self):
        self.account.is_fast = True
        self.account.save()
        self.check_ajax_error(self.client.post(reverse('forum:subscriptions:')),
                              'common.fast_account')

    def test_empty(self):
        texts = [('thread1-caption', 0),
                 ('thread2-caption', 0),
                 ('thread3-caption', 0),
                 ('subcat1-caption', 0),
                 ('subcat2-caption', 0),
                 ('pgf-no-thread-subscriptions-message', 1),
                 ('pgf-no-subcategory-subscriptions-message', 1)]
        self.check_html_ok(self.client.get(reverse('forum:subscriptions:'), texts=texts))

    def test_subscriptions(self):
        self.check_ajax_ok(self.client.post(reverse('forum:subscriptions:subscribe')+('?thread=%d' % self.thread1.id)))
        self.check_ajax_ok(self.client.post(reverse('forum:subscriptions:subscribe')+('?thread=%d' % self.thread3.id)))
        self.check_ajax_ok(self.client.post(reverse('forum:subscriptions:subscribe')+('?subcategory=%d' % self.subcat2.id)))

        texts = [('thread1-caption', 1),
                 ('thread2-caption', 0),
                 ('thread3-caption', 1),
                 ('subcat1-caption', 0),
                 ('subcat2-caption', 1),
                 ('pgf-no-thread-subscriptions-message', 0),
                 ('pgf-no-subcategory-subscriptions-message', 0)]
        self.check_html_ok(self.client.get(reverse('forum:subscriptions:'), texts=texts))
