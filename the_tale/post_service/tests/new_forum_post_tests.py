# coding: utf-8

from django.core import mail
from django.conf import settings as project_settings

from common.utils import testcase

from accounts.logic import register_user
from accounts.prototypes import AccountPrototype

from game.logic import create_test_map

from forum.prototypes import ThreadPrototype, SubCategoryPrototype, CategoryPrototype, SubscriptionPrototype, PostPrototype

from post_service.models import Message
from post_service.prototypes import MessagePrototype


class NewForumPostTests(testcase.TestCase):

    def setUp(self):
        super(NewForumPostTests, self).setUp()
        create_test_map()

        register_user('user_1', 'user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_nick('user_1')

        self.category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = SubCategoryPrototype.create(category=self.category, caption='subcat-caption', slug='subcat-slug', order=0)
        self.thread = ThreadPrototype.create(self.subcategory, 'thread_1-caption', self.account_1, 'thread-text')

        self.post = PostPrototype.create(self.thread, self.account_1, 'post-text')

        self.message = MessagePrototype.get_priority_message()


    def test_register_message(self):
        self.assertEqual(Message.objects.all().count(), 1)

    def test_no_subscriptions(self):
        self.assertEqual(len(mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state._is_PROCESSED)
        self.assertEqual(len(mail.outbox), 0)

    def test_one_subscription(self):
        SubscriptionPrototype.create(self.account_1, self.thread)
        self.assertEqual(len(mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state._is_PROCESSED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.account_1.email])

        self.assertTrue(self.post.author.nick in mail.outbox[0].body)
        self.assertTrue(self.post.thread.caption in mail.outbox[0].body)
        self.assertTrue(self.post.thread.paginator.last_page_url in mail.outbox[0].body)
        self.assertTrue(project_settings.SITE_URL in mail.outbox[0].body)

        self.assertTrue(self.post.author.nick in mail.outbox[0].alternatives[0][0])
        self.assertTrue(self.post.thread.caption in mail.outbox[0].alternatives[0][0])
        self.assertTrue(self.post.thread.paginator.last_page_url in mail.outbox[0].alternatives[0][0])
        self.assertTrue(project_settings.SITE_URL in mail.outbox[0].alternatives[0][0])

    def test_many_subscriptions(self):
        register_user('user_2', 'user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_nick('user_2')

        SubscriptionPrototype.create(self.account_1, self.thread)
        SubscriptionPrototype.create(account_2, self.thread)

        self.assertEqual(len(mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state._is_PROCESSED)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, [self.account_1.email])
        self.assertEqual(mail.outbox[1].to, [account_2.email])
