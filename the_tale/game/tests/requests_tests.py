# coding: utf-8
import datetime

from django.test import client
from django.core.urlresolvers import reverse

from dext.utils import s11n

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, login_url

from game.logic import create_test_map
from game.pvp.models import BATTLE_1X1_STATE

from game.pvp.tests.helpers import PvPTestsMixin

from cms.news.models import News

class TestRequests(TestCase, PvPTestsMixin):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account_1_id = account_id
        self.account_1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2_id = account_id
        self.account_2 = AccountPrototype.get_by_id(account_id)

        self.client = client.Client()


    def test_game_page_unlogined(self):
        self.check_redirect(reverse('game:'), login_url(reverse('game:')))

    def test_game_page_logined(self):
        self.request_login('test_user@test.com')
        response = self.client.get(reverse('game:'))
        self.assertEqual(response.status_code, 200)

    def test_info_unlogined(self):
        self.check_redirect(reverse('game:info'), login_url(reverse('game:info')))

    def test_info_logined(self):
        self.request_login('test_user@test.com')
        response = self.client.get(reverse('game:info'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(s11n.from_json(response.content)['data'].keys()), set(('turn', 'hero', 'abilities', 'mode', 'pvp')))

    def test_info_other_account(self):
        self.request_login('test_user@test.com')
        response = self.client.get(reverse('game:info') + ('?account=%s' % self.account_2_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(s11n.from_json(response.content)['data'].keys()), set(('turn', 'hero', 'mode')))

    def test_info_account_not_exists(self):
        self.request_login('test_user@test.com')
        response = self.client.get(reverse('game:info') + '?account=666')
        self.check_ajax_error(response, 'game.info.account_not_exists')

    def test_info_wrong_account_id(self):
        self.request_login('test_user@test.com')
        response = self.client.get(reverse('game:info') + '?account=sdsd')
        self.check_ajax_error(response, 'game.info.wrong_account_id')


    def test_game_page_when_pvp_in_queue(self):
        self.pvp_create_battle(self.account_1, self.account_2)
        self.pvp_create_battle(self.account_2, self.account_1)
        self.request_login('test_user@test.com')
        self.check_html_ok(self.client.get(reverse('game:')))

    def test_game_page_when_pvp_processing(self):
        self.pvp_create_battle(self.account_1, self.account_2, BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, BATTLE_1X1_STATE.PROCESSING)
        self.request_login('test_user@test.com')
        self.check_redirect(reverse('game:'), reverse('game:pvp:'))

    def test_game_info_when_pvp_in_queue(self):
        self.pvp_create_battle(self.account_1, None)
        self.pvp_create_battle(self.account_2, None)
        self.request_login('test_user@test.com')
        self.assertEqual(s11n.from_json(self.client.get(reverse('game:info')).content)['data']['mode'], 'pve')

    def test_game_info_when_pvp_prepairing(self):
        self.pvp_create_battle(self.account_1, self.account_2)
        self.pvp_create_battle(self.account_2, self.account_1)
        self.request_login('test_user@test.com')
        self.assertEqual(s11n.from_json(self.client.get(reverse('game:info')).content)['data']['mode'], 'pvp')

    def test_game_info_when_pvp_processing(self):
        self.pvp_create_battle(self.account_1, self.account_2, BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, BATTLE_1X1_STATE.PROCESSING)
        self.request_login('test_user@test.com')
        self.assertEqual(s11n.from_json(self.client.get(reverse('game:info')).content)['data']['mode'], 'pvp')


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

    def test_news_alert_for_new_account(self):
        self.check_reminder(reverse('game:'), 0, 0, 0)

    def test_news_alert(self):
        self.account.last_news_remind_time -= datetime.timedelta(seconds=666)
        self.account.save()

        self.check_reminder(reverse('game:'), 1, 1, 2)

    def test_no_news_alert(self):
        self.account.last_news_remind_time = datetime.datetime.now()
        self.account.save()
        self.check_reminder(reverse('game:'), 0, 0, 0)
