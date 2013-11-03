# coding: utf-8

import mock

import datetime

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map

from the_tale.forum.prototypes import ThreadPrototype, SubCategoryPrototype, ThreadReadInfoPrototype, CategoryPrototype, SubCategoryReadInfoPrototype
from the_tale.forum.read_state import ReadState
from the_tale.forum.exceptions import ForumException


class ReadStateTests(testcase.TestCase):

    def setUp(self):
        super(ReadStateTests, self).setUp()
        create_test_map()

        register_user('user_1', 'user_1@test.com', '111111')
        register_user('user_2', 'user_2@test.com', '111111')

        self.account = AccountPrototype.get_by_nick('user_1')
        self.account_2 = AccountPrototype.get_by_nick('user_2')

        category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = SubCategoryPrototype.create(category=category, caption='subcat-caption', order=0)
        self.subcategory_2 = SubCategoryPrototype.create(category=category, caption='subcat-2-caption', order=0)

        self.thread = ThreadPrototype.create(self.subcategory, 'thread1-caption', self.account_2, 'thread-text')
        self.thread_2 = ThreadPrototype.create(self.subcategory, 'thread2-caption', self.account_2, 'thread-2-text')
        self.thread_3 = ThreadPrototype.create(self.subcategory_2, 'thread2-caption', self.account, 'thread-2-text')

    def get_read_state(self, account=None):
        return ReadState(self.account if account is None else account,
                         threads=[self.thread, self.thread_2],
                         subcategory=self.subcategory)

    def test_threads_from_different_subcategories(self, account=None):
        self.assertRaises(ForumException,
                          ReadState,
                          self.account if account is None else account,
                          threads=[self.thread, self.thread_2, self.thread_3],
                          subcategory=self.subcategory)

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', lambda a: False)
    def test_thread_has_new_messages__unauthenticated(self):
        read_state = self.get_read_state()
        self.assertFalse(read_state.thread_has_new_messages(self.thread))

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', lambda a: True)
    def test_thread_has_new_messages__never_read(self):
        read_state = self.get_read_state()
        self.assertTrue(read_state.thread_has_new_messages(self.thread))
        self.account._model.created_at = datetime.datetime.now()
        self.account.save()
        self.assertFalse(read_state.thread_has_new_messages(self.thread))

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', lambda a: True)
    def test_thread_has_new_messages__read(self):
        ThreadReadInfoPrototype.read_thread(self.thread, self.account)

        read_state = self.get_read_state()

        self.assertFalse(read_state.thread_has_new_messages(self.thread))

        self.thread._model.updated_at = datetime.datetime.now()
        self.thread.save()

        self.assertTrue(read_state.thread_has_new_messages(self.thread))

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', lambda a: True)
    @mock.patch('the_tale.forum.conf.forum_settings.UNREAD_STATE_EXPIRE_TIME', 0)
    def test_thread_has_new_messages__unread_state_expired(self):
        read_state = self.get_read_state()
        self.assertFalse(read_state.thread_has_new_messages(self.thread))


    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', lambda a: False)
    def test_thread_is_new__unauthenticated(self):
        read_state = self.get_read_state()
        self.assertFalse(read_state.thread_is_new(self.thread))

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', lambda a: True)
    def test_thread_is_new__author(self):
        read_state = self.get_read_state(account=self.account_2)
        self.assertFalse(read_state.thread_is_new(self.thread))

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', lambda a: True)
    def test_thread_is_new__never_read(self):
        read_state = self.get_read_state()
        self.assertTrue(read_state.thread_is_new(self.thread))
        self.account._model.created_at = datetime.datetime.now()
        self.account.save()
        self.assertFalse(read_state.thread_is_new(self.thread))

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', lambda a: True)
    def test_thread_is_new__read(self):
        SubCategoryReadInfoPrototype.read_subcategory(self.subcategory, self.account)

        read_state = self.get_read_state()

        self.assertFalse(read_state.thread_is_new(self.thread))

        self.thread._model.created_at = datetime.datetime.now()
        self.thread.save()

        self.assertTrue(read_state.thread_is_new(self.thread))

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', lambda a: True)
    @mock.patch('the_tale.forum.conf.forum_settings.UNREAD_STATE_EXPIRE_TIME', 0)
    def test_thread_is_new__unread_state_expired(self):
        read_state = self.get_read_state()
        self.assertFalse(read_state.thread_is_new(self.thread))

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', lambda a: True)
    def test_thread_has_new_messages__category_read(self):
        read_state = self.get_read_state()
        self.assertTrue(read_state.thread_is_new(self.thread))

        SubCategoryReadInfoPrototype.read_all_in_subcategory(self.subcategory, self.account)
        read_state = self.get_read_state()

        self.assertFalse(read_state.thread_has_new_messages(self.thread))

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_authenticated', lambda a: True)
    def test_thread_is_new_messages__thread_read(self):
        read_state = self.get_read_state()
        self.assertTrue(read_state.thread_is_new(self.thread))

        ThreadReadInfoPrototype.read_thread(self.thread, self.account)
        read_state = self.get_read_state()

        self.assertFalse(read_state.thread_is_new(self.thread))
