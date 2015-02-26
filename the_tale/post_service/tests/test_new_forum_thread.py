# coding: utf-8

from django.core import mail
from django.conf import settings as project_settings

from dext import jinja2 as dext_jinja2

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic import create_test_map

from the_tale.forum.prototypes import ThreadPrototype, SubCategoryPrototype, CategoryPrototype, SubscriptionPrototype

from the_tale.post_service.models import Message
from the_tale.post_service.prototypes import MessagePrototype


class NewForumThreadTests(testcase.TestCase):

    def setUp(self):
        super(NewForumThreadTests, self).setUp()
        create_test_map()

        register_user('user_1', 'user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_nick('user_1')

        self.category = CategoryPrototype.create(caption='cat-caption', slug='cat-slug', order=0)
        self.subcategory = SubCategoryPrototype.create(category=self.category, caption='subcat-caption', order=0)
        self.thread = ThreadPrototype.create(self.subcategory, 'thread_1-caption', self.account_1, 'thread-text')

        self.message = MessagePrototype.get_priority_message()

        dext_jinja2.autodiscover()


    def test_register_message(self):
        self.assertEqual(Message.objects.all().count(), 1)

    def test_no_subscriptions(self):
        self.assertEqual(len(mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state.is_PROCESSED)
        self.assertEqual(len(mail.outbox), 0)

    def test_one_subscription(self):
        SubscriptionPrototype.create(self.account_1, subcategory=self.subcategory)
        self.assertEqual(len(mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state.is_PROCESSED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.account_1.email])

        self.assertTrue(self.thread.author.nick in mail.outbox[0].body)
        self.assertTrue(self.thread.caption in mail.outbox[0].body)
        self.assertTrue(self.thread.paginator.last_page_url in mail.outbox[0].body)
        self.assertTrue(self.thread.get_first_post().html in mail.outbox[0].body)
        self.assertTrue(project_settings.SITE_URL in mail.outbox[0].body)

        self.assertTrue(self.thread.author.nick in mail.outbox[0].alternatives[0][0])
        self.assertTrue(self.thread.caption in mail.outbox[0].alternatives[0][0])
        self.assertTrue(self.thread.paginator.last_page_url in mail.outbox[0].alternatives[0][0])
        self.assertTrue(self.thread.get_first_post().html in mail.outbox[0].alternatives[0][0])
        self.assertTrue(project_settings.SITE_URL in mail.outbox[0].alternatives[0][0])

    def test_mail_send__to_system_user(self):
        from the_tale.accounts.logic import get_system_user

        SubscriptionPrototype.create(get_system_user(), subcategory=self.subcategory)
        self.assertEqual(len(mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state.is_PROCESSED)
        self.assertEqual(len(mail.outbox), 0)

    def test_many_subscriptions(self):
        register_user('user_2', 'user_2@test.com', '111111')
        account_2 = AccountPrototype.get_by_nick('user_2')

        SubscriptionPrototype.create(self.account_1, subcategory=self.subcategory)
        SubscriptionPrototype.create(account_2, subcategory=self.subcategory)

        self.assertEqual(len(mail.outbox), 0)
        self.message.process()
        self.assertTrue(self.message.state.is_PROCESSED)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, [self.account_1.email])
        self.assertEqual(mail.outbox[1].to, [account_2.email])
