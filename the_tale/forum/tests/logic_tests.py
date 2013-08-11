# coding: utf-8

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user
from game.logic import create_test_map

from forum.prototypes import ThreadPrototype, PostPrototype, SubCategoryPrototype, CategoryPrototype

class TestGetThreadsWithLastUsersPosts(TestCase):

    def setUp(self):
        super(TestGetThreadsWithLastUsersPosts, self).setUp()
        create_test_map()

        register_user('user_1', 'user_1@test.com', '111111')
        register_user('user_2', 'user_2@test.com', '111111')
        register_user('user_3', 'user_3@test.com', '111111')
        register_user('user_4', 'user_4@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_nick('user_1')
        self.account_2 = AccountPrototype.get_by_nick('user_2')
        self.account_3 = AccountPrototype.get_by_nick('user_3')
        self.account_4 = AccountPrototype.get_by_nick('user_4')


        self.category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = SubCategoryPrototype.create(category=self.category, caption='subcat-caption', order=0)

        self.thread1 = ThreadPrototype.create(self.subcategory, 'thread1-caption', self.account_1, 'thread-text')

        # posts in thread 1
        self.post1 = PostPrototype.create(self.thread1, self.account_1, 'post-text')
        self.post2 = PostPrototype.create(self.thread1, self.account_1, 'post2-text')

        self.thread2 = ThreadPrototype.create(self.subcategory, 'thread2-caption', self.account_1, 'thread2-text')


        self.thread3 = ThreadPrototype.create(self.subcategory, 'thread3-caption', self.account_2, 'thread3-text')

        self.post4 = PostPrototype.create(self.thread2, self.account_2, 'post4-text')

        self.post5 = PostPrototype.create(self.thread3, self.account_1, 'post5-text')
        self.post6 = PostPrototype.create(self.thread3, self.account_2, 'post6-text')
        self.post7 = PostPrototype.create(self.thread3, self.account_3, 'post7-text')

        self.post3 = PostPrototype.create(self.thread2, self.account_1, 'post3-text')


    def test_no_posts(self):
        self.assertEqual(list(ThreadPrototype.get_threads_with_last_users_posts(self.account_4)), [])
        self.assertEqual(list(ThreadPrototype.get_threads_with_last_users_posts(self.account_4, limit=5)), [])

    def test_success(self):
        self.assertEqual([ thread.id for thread in ThreadPrototype.get_threads_with_last_users_posts(self.account_1, limit=2)],
                         [self.thread2.id, self.thread3.id])

        self.assertEqual([ thread.id for thread in ThreadPrototype.get_threads_with_last_users_posts(self.account_1)],
                         [self.thread2.id, self.thread3.id, self.thread1.id])

        self.assertEqual([ thread.id for thread in ThreadPrototype.get_threads_with_last_users_posts(self.account_2)],
                         [self.thread3.id, self.thread2.id])
