# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate as django_authenticate

from common.utils.testcase import TestCase
from common.utils.permissions import sync_group

from accounts.logic import register_user
from game.logic import create_test_map

from forum.models import Category, SubCategory, Thread, Post
from forum.logic import create_thread, create_post

class TestGetThreadsWithLastUsersPosts(TestCase):

    def setUp(self):
        create_test_map()

        register_user('user_1', 'user_1@test.com', '111111')
        register_user('user_2', 'user_2@test.com', '111111')
        register_user('user_3', 'user_3@test.com', '111111')

        self.user_1 = django_authenticate(username='user_1', password='111111')
        self.user_2 = django_authenticate(username='user_2', password='111111')
        self.user_3 = django_authenticate(username='user_3', password='111111')
        self.user_4 = django_authenticate(username='user_4', password='111111')


        self.category = Category.objects.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = SubCategory.objects.create(category=self.category, caption='subcat-caption', slug='subcat-slug', order=0)

        self.thread1 = create_thread(self.subcategory, 'thread1-caption', self.user_1, 'thread-text')

        # posts in thread 1
        self.post1 = create_post(self.subcategory, self.thread1, self.user_1, 'post-text')
        self.post2 = create_post(self.subcategory, self.thread1, self.user_1, 'post2-text')

        self.thread2 = create_thread(self.subcategory, 'thread2-caption', self.user_1, 'thread2-text')


        self.thread3 = create_thread(self.subcategory, 'thread3-caption', self.user_2, 'thread3-text')

        self.post4 = create_post(self.subcategory, self.thread2, self.user_2, 'post4-text')

        self.post5 = create_post(self.subcategory, self.thread3, self.user_1, 'post5-text')
        self.post6 = create_post(self.subcategory, self.thread3, self.user_2, 'post6-text')
        self.post7 = create_post(self.subcategory, self.thread3, self.user_3, 'post7-text')

        self.post3 = create_post(self.subcategory, self.thread2, self.user_1, 'post3-text')


    def test_no_posts(self):
        self.assertEqual(list(Thread.get_threads_with_last_users_posts(self.user_4)), [])
        self.assertEqual(list(Thread.get_threads_with_last_users_posts(self.user_4, limit=5)), [])

    def test_success(self):
        self.assertEqual([ thread.id for thread in Thread.get_threads_with_last_users_posts(self.user_1, limit=2)],
                         [self.thread2.id, self.thread3.id])

        self.assertEqual([ thread.id for thread in Thread.get_threads_with_last_users_posts(self.user_1)],
                         [self.thread2.id, self.thread3.id, self.thread1.id])

        self.assertEqual([ thread.id for thread in Thread.get_threads_with_last_users_posts(self.user_2)],
                         [self.thread3.id, self.thread2.id])
