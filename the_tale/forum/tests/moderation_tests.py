# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate as django_authenticate

from dext.utils import s11n

from common.utils.testcase import TestCase
from common.utils.permissions import sync_group

from accounts.logic import register_user
from game.logic import create_test_map

from forum.models import Category, SubCategory, Thread, Post
from forum.logic import create_thread, create_post
from forum.conf import forum_settings

class TestModeration(TestCase):

    def setUp(self):
        create_test_map()
        register_user('main_user', 'main_user@test.com', '111111')
        register_user('moderator', 'moderator@test.com', '111111')
        register_user('second_user', 'second_user@test.com', '111111')

        self.main_user = django_authenticate(username='main_user', password='111111')
        self.moderator = django_authenticate(username='moderator', password='111111')
        self.second_user = django_authenticate(username='second_user', password='111111')

        group = sync_group('forum moderators group', ['forum.add_thread', 'forum.change_thread', 'forum.delete_thread',
                                                      'forum.add_post',  'forum.change_post', 'forum.delete_post'])

        group.user_set.add(self.moderator)

        self.client = client.Client()

        self.category = Category.objects.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = SubCategory.objects.create(category=self.category, caption='subcat-caption', slug='subcat-slug', order=0)
        self.thread = create_thread(self.subcategory, 'thread-caption', self.main_user, 'thread-text')
        self.post = create_post(self.subcategory, self.thread, self.main_user, 'post-text')
        self.post = create_post(self.subcategory, self.thread, self.main_user, 'post2-text')

        self.thread2 = create_thread(self.subcategory, 'thread2-caption', self.main_user, 'thread2-text')
        self.post2 = create_post(self.subcategory, self.thread2, self.main_user, 'post3-text')


    def login(self, user_name):
        response = self.client.post(reverse('accounts:login'), {'email': '%s@test.com' % user_name, 'password': '111111'})
        self.assertEqual(response.status_code, 200)

    def logout(self):
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 200)

    def test_initialization(self):
        self.assertEqual(Category.objects.all().count(), 1)
        self.assertEqual(SubCategory.objects.all().count(), 1)
        self.assertEqual(Thread.objects.all().count(), 2)
        self.assertEqual(Post.objects.all().count(), 5)

    def test_main_user_has_remove_thread_button(self):
        self.login('main_user')
        self.check_html_ok(self.client.get(reverse('forum:show_thread', args=['cat-slug', 'subcat-slug', self.thread.id])), texts=['pgf-remove-thread-button'])

    def test_moderator_has_remove_thread_button(self):
        self.login('moderator')
        self.check_html_ok(self.client.get(reverse('forum:show_thread', args=['cat-slug', 'subcat-slug', self.thread.id])), texts=['pgf-remove-thread-button'])

    def test_second_user_has_remove_thread_button(self):
        self.login('second_user')
        self.check_html_ok(self.client.get(reverse('forum:show_thread', args=['cat-slug', 'subcat-slug', self.thread.id])), excluded_texts=['pgf-remove-thread-button'])

    def test_main_user_remove_thread(self):
        self.login('main_user')
        self.check_ajax_ok(self.client.post(reverse('forum:delete-thread', args=['cat-slug', 'subcat-slug', self.thread.id])))
        self.assertEqual(Thread.objects.all().count(), 1)
        self.assertEqual(Post.objects.all().count(), 2)

    def test_moderator_remove_thread(self):
        self.login('moderator')
        self.check_ajax_ok(self.client.post(reverse('forum:delete-thread', args=['cat-slug', 'subcat-slug', self.thread.id])))
        self.assertEqual(Thread.objects.all().count(), 1)
        self.assertEqual(Post.objects.all().count(), 2)

    def test_second_user_remove_thread(self):
        self.login('second_user')
        self.check_ajax_error(self.client.post(reverse('forum:delete-thread', args=['cat-slug', 'subcat-slug', self.thread.id])), 'forum.delete_thread.no_permissions')
        self.assertEqual(Thread.objects.all().count(), 2)
        self.assertEqual(Post.objects.all().count(), 5)

    def test_second_user_remove_unlogined(self):
        self.check_ajax_error(self.client.post(reverse('forum:delete-thread', args=['cat-slug', 'subcat-slug', self.thread.id])), 'forum.delete_thread.unlogined')
        self.assertEqual(Thread.objects.all().count(), 2)
        self.assertEqual(Post.objects.all().count(), 5)

    def test_second_user_remove_fast_account(self):
        self.login('main_user')

        account = self.main_user.get_profile()
        account.is_fast = True
        account.save()

        self.check_ajax_error(self.client.post(reverse('forum:delete-thread', args=['cat-slug', 'subcat-slug', self.thread.id])), 'forum.delete_thread.fast_account')
        self.assertEqual(Thread.objects.all().count(), 2)
        self.assertEqual(Post.objects.all().count(), 5)
