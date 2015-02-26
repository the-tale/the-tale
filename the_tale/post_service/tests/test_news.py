# coding: utf-8

from django.core import mail
from django.conf import settings as project_settings

from dext import jinja2 as dext_jinja2

from the_tale.common.utils import testcase

from the_tale.accounts import logic as accounts_logic

from the_tale.game.logic import create_test_map

from the_tale.post_service.models import Message
from the_tale.post_service.prototypes import MessagePrototype

from the_tale.cms.news import logic as news_logic


class NewNewsTests(testcase.TestCase):

    def setUp(self):
        super(NewNewsTests, self).setUp()
        create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()

        self.news = news_logic.create_news(caption='news-caption', description='news-description', content='news-content')

        news_logic.send_mails(self.news)

        self.message = MessagePrototype.get_priority_message()

        # enshure that system user exists
        accounts_logic.get_system_user()

        dext_jinja2.autodiscover()

    def test_register_message(self):
        self.assertEqual(Message.objects.all().count(), 1)

    def test_no_subscription(self):
        self.account_2.news_subscription = False
        self.account_2.save()

        with self.check_delta(mail.outbox.__len__, 2):
            self.message.process()

        self.assertTrue(self.message.state.is_PROCESSED)

        self.assertEqual(mail.outbox[0].to, [self.account_1.email])
        self.assertEqual(mail.outbox[1].to, [self.account_3.email])

        self.assertTrue(self.news.caption in mail.outbox[0].body)
        self.assertTrue(project_settings.SITE_URL in mail.outbox[0].body)

        self.assertTrue(self.news.caption in mail.outbox[0].alternatives[0][0])
        self.assertTrue(project_settings.SITE_URL in mail.outbox[0].alternatives[0][0])
