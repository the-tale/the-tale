# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate as django_authenticate

from common.utils.testcase import TestCase

from accounts.logic import register_user
from game.logic import create_test_map

from forum.models import Category, SubCategory, Thread, Post
from forum.logic import create_thread, create_post
from forum.conf import forum_settings

class TestRequests(TestCase):

    def setUp(self):
        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')

        self.user = django_authenticate(username='test_user', password='111111')

        self.client = client.Client()
        self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})

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

        self.cat1 = Category.objects.create(caption='cat1-caption', slug='cat1-slug', order=0)
        # to test, that subcat.id not correlate with order
        self.subcat2 = SubCategory.objects.create(category=self.cat1, caption='subcat2-caption', slug='subcat2-slug', order=1, closed=True)
        self.subcat1 = SubCategory.objects.create(category=self.cat1, caption='subcat1-caption', slug='subcat1-slug', order=0)
        self.cat2 = Category.objects.create(caption='cat2-caption', slug='cat2-slug', order=0)
        self.subcat3 = SubCategory.objects.create(category=self.cat2, caption='subcat3-caption', slug='subcat3-slug', order=0)
        self.cat3 = Category.objects.create(caption='cat3-caption', slug='cat3-slug', order=0)

        self.thread1 = create_thread(self.subcat1, 'thread1-caption', self.user, 'thread1-text')
        self.thread2 = create_thread(self.subcat1, 'thread2-caption', self.user, 'thread2-text')
        self.thread3 = create_thread(self.subcat3, 'thread3-caption', self.user, 'thread3-text')

        self.post1 = create_post(self.subcat1, self.thread1, self.user, 'post1-text')


    def logout(self):
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 200)

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
        self.logout()
        self.check_html_ok(self.client.get(reverse('forum:')), texts=texts)

    def test_subcategory(self):
        texts=['cat1-caption', 'subcat1-caption', 'thread1-caption', 'thread2-caption']
        self.check_html_ok(self.client.get(reverse('forum:subcategory', args=['subcat1-slug'])), texts=texts)
        self.logout()
        self.check_html_ok(self.client.get(reverse('forum:subcategory', args=['subcat1-slug'])), texts=texts)

    def test_new_thread(self):
        texts=['cat1-caption', 'subcat1-caption']
        self.check_html_ok(self.client.get(reverse('forum:new-thread', args=['subcat1-slug'])), texts=texts)

    def test_new_thread_unlogined(self):
        self.logout()
        self.check_html_ok(self.client.get(reverse('forum:new-thread', args=['subcat1-slug'])), texts=['pgf-error-forum.new_thread.unlogined'])

    def test_new_thread_fast(self):
        account = self.user.get_profile()
        account.is_fast = True
        account.save()
        self.check_html_ok(self.client.get(reverse('forum:new-thread', args=['subcat1-slug'])), texts=['pgf-error-forum.new_thread.fast_account'])

    def test_create_thread_unlogined(self):
        self.logout()
        self.check_ajax_error(self.client.post(reverse('forum:create-thread', args=['subcat1-slug'])),
                              code='forum.create_thread.unlogined')

    def test_create_thread_fast_account(self):
        account = self.user.get_profile()
        account.is_fast = True
        account.save()
        self.check_ajax_error(self.client.post(reverse('forum:create-thread', args=['subcat1-slug'])),
                              code='forum.create_thread.fast_account')

    def test_create_thread_closed_subcategory(self):
        self.check_ajax_error(self.client.post(reverse('forum:create-thread', args=['subcat2-slug'])),
                              code='forum.create_thread.no_permissions')

    def test_create_thread_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('forum:create-thread', args=['subcat1-slug'])),
                              code='forum.create_thread.form_errors')

    def test_create_thread_success(self):
        response = self.client.post(reverse('forum:create-thread', args=['subcat1-slug']), {'caption': 'thread4-caption', 'text': 'thread4-text'})

        thread = Thread.objects.all().order_by('-created_at')[0]

        self.check_ajax_ok(response, {'thread_id': thread.id,
                                      'thread_url': reverse('forum:show-thread', args=[thread.id])})

        self.assertEqual(thread.posts_count, 0)
        self.assertEqual(thread.caption, 'thread4-caption')
        self.assertEqual(thread.author, self.user)

        post = Post.objects.filter(thread=thread)[0]
        self.assertEqual(post.text, 'thread4-text')
        self.assertEqual(post.author, self.user)

        self.assertEqual(Thread.objects.all().count(), 4)
        self.assertEqual(Post.objects.all().count(), 5)

        self.assertEqual(SubCategory.objects.get(id=self.subcat1.id).posts_count, 1)

    def test_get_thread_unlogined(self):
        excluded_texts = ['pgf-new-post-form']
        self.logout()
        self.check_html_ok(self.client.get(reverse('forum:show-thread', args=[self.thread1.id])), excluded_texts=excluded_texts)

    def test_get_thread_fast_account(self):
        excluded_texts = ['pgf-new-post-form']
        account = self.user.get_profile()
        account.is_fast = True
        account.save()
        self.check_html_ok(self.client.get(reverse('forum:show-thread', args=[self.thread1.id])), excluded_texts=excluded_texts)

    def test_get_thread_wrong_page(self):
        response = self.client.get(reverse('forum:show-thread', args=[self.thread1.id])+'?page=2')
        self.assertRedirects(response, reverse('forum:show-thread', args=[self.thread1.id])+'?page=1', status_code=302, target_status_code=200)

    def test_get_thread_with_pagination(self):

        texts = []

        for i in xrange(forum_settings.POSTS_ON_PAGE-1):
            text = 'subcat3-post%d-text' % i
            create_post(self.subcat3, self.thread3, self.user, text)
            texts.append(text)

        response = self.client.get(reverse('forum:show-thread', args=[self.thread3.id])+'?page=2')
        self.assertRedirects(response, reverse('forum:show-thread', args=[self.thread3.id])+'?page=1', status_code=302, target_status_code=200)

        self.check_html_ok(self.client.get(reverse('forum:show-thread', args=[self.thread3.id])), texts=texts)

        ++i
        text = 'subcat3-post%d-text' % i
        create_post(self.subcat3, self.thread3, self.user, text)
        texts.append(text)

        self.check_html_ok(self.client.get(reverse('forum:show-thread', args=[self.thread3.id])+'?page=1', texts=texts))
        response = self.client.get(reverse('forum:show-thread', args=[self.thread3.id])+'?page=2', texts=[text])

    def test_posts_count(self):
        for i in xrange(4):
            create_post(self.subcat1, self.thread1, self.user, 'subcat1-thread1-post%d-text' % i)

        for i in xrange(7):
            create_post(self.subcat1, self.thread2, self.user, 'subcat1-thread2-post%d-text' % i)

        # first post in thread does not count
        self.assertEqual(SubCategory.objects.get(id=self.subcat1.id).posts_count, 12)
        self.assertEqual(Thread.objects.get(id=self.thread1.id).posts_count, 5)
        self.assertEqual(Thread.objects.get(id=self.thread2.id).posts_count, 7)

    def test_create_post_unlogined(self):
        self.logout()
        self.check_ajax_error(self.client.post(reverse('forum:create-post', args=[self.thread3.id])),
                              code='forum.create_post.unlogined')

    def test_create_post_fast_account(self):
        account = self.user.get_profile()
        account.is_fast = True
        account.save()
        self.check_ajax_error(self.client.post(reverse('forum:create-post', args=[self.thread3.id])),
                              code='forum.create_post.fast_account')

    def test_create_post_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('forum:create-post', args=[self.thread3.id])),
                              code='forum.create_post.form_errors')

    def test_create_post_success(self):
        self.check_ajax_ok(self.client.post(reverse('forum:create-post', args=[self.thread3.id]), {'text': 'thread3-test-post'}))
        self.assertEqual(Post.objects.all().count(), 5)

    def test_preview(self):
        text = 'simple test text'
        self.check_html_ok(self.client.post(reverse('forum:preview'), {'text': text}), texts=[text])
