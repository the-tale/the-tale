# coding: utf-8
import datetime

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase

from game.logic import create_test_map

from accounts.logic import register_user
from accounts.prototypes import AccountPrototype

from cms.news.models import News

class TestRequests(TestCase):

    def setUp(self):
        create_test_map()
        self.client = client.Client()

    def test_index(self):
        response = self.client.get(reverse('portal:'))
        self.assertEqual(response.status_code, 200)

    def test_preview(self):
        text = 'simple test text'
        self.check_html_ok(self.client.post(reverse('portal:preview'), {'text': text}), texts=[text])

class NewsAlertsTests(TestCase):

    def setUp(self):
        create_test_map()
        self.client = client.Client()

        self.news = News.objects.create(caption='news-caption', description='news-description', content='news-content')

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        self.request_login('test_user@test.com')

    def check_reminder(self, url, caption, description, block):
        self.check_html_ok(self.client.get(url), texts=[('news-caption', caption),
                                                        ('news-description', description),
                                                        ('news-content', 0),
                                                        ('pgf-last-news-reminder', block)])

    def test_news_alert_unlogined(self):
        self.request_logout()
        self.check_reminder(reverse('guide:game'), 0, 0, 0)

    def test_news_alert(self):
        self.check_reminder(reverse('guide:game'), 1, 1, 2)

    def test_no_news_alert(self):
        self.account.last_news_remind_time = datetime.datetime.now()
        self.account.save()
        self.check_reminder(reverse('guide:game'), 0, 0, 0)

    def test_no_news_alert_on_index(self):
        self.check_reminder(reverse('portal:'), 1, 1, 0)
