# coding: utf-8
import datetime

import mock

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

class RequestTestsBase(TestCase, PvPTestsMixin):

    def setUp(self):
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account_1_id = account_id
        self.account_1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2_id = account_id
        self.account_2 = AccountPrototype.get_by_id(account_id)

        self.client = client.Client()

        self.game_info_url_1 = reverse('game:info') + ('?account=%d' % self.account_1.id)
        self.game_info_url_2 = reverse('game:info') + ('?account=%d' % self.account_2.id)

        self.request_login('test_user@test.com')

class GamePageRequestTests(RequestTestsBase):

    def test_game_page_unlogined(self):
        self.request_logout()
        self.check_redirect(reverse('game:'), login_url(reverse('game:')))

    def test_game_page_logined(self):
        response = self.client.get(reverse('game:'))
        self.assertEqual(response.status_code, 200)

    def test_game_page_when_pvp_in_queue(self):
        self.pvp_create_battle(self.account_1, self.account_2)
        self.pvp_create_battle(self.account_2, self.account_1)
        self.check_html_ok(self.client.get(reverse('game:')))

    def test_game_page_when_pvp_processing(self):
        self.pvp_create_battle(self.account_1, self.account_2, BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, BATTLE_1X1_STATE.PROCESSING)
        self.check_redirect(reverse('game:'), reverse('game:pvp:'))


class InfoRequestTests(RequestTestsBase):

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_ok(self.client.get(self.game_info_url_1, HTTP_X_REQUESTED_WITH='XMLHttpRequest'))

    def test_logined(self):
        response = self.client.get(self.game_info_url_1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(s11n.from_json(response.content)['data'].keys()), set(('turn', 'hero', 'abilities', 'mode', 'pvp')))

    def test_other_account(self):
        response = self.client.get(self.game_info_url_2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(s11n.from_json(response.content)['data'].keys()), set(('turn', 'hero', 'mode')))

    def test_account_not_exists(self):
        response = self.client.get(reverse('game:info') + '?account=666', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.check_ajax_error(response, 'game.info.account.not_found')

    def test_wrong_account_id(self):
        response = self.client.get(reverse('game:info') + '?account=sdsd', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.check_ajax_error(response, 'game.info.account.wrong_format')

    def test_pvp_in_queue(self):
        self.pvp_create_battle(self.account_1, None)
        self.pvp_create_battle(self.account_2, None)
        self.assertEqual(s11n.from_json(self.client.get(self.game_info_url_1).content)['data']['mode'], 'pve')

    def test_pvp_prepairing(self):
        self.pvp_create_battle(self.account_1, self.account_2)
        self.pvp_create_battle(self.account_2, self.account_1)
        self.assertEqual(s11n.from_json(self.client.get(self.game_info_url_1).content)['data']['mode'], 'pvp')

    def test_pvp_processing(self):
        self.pvp_create_battle(self.account_1, self.account_2, BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, BATTLE_1X1_STATE.PROCESSING)
        self.assertEqual(s11n.from_json(self.client.get(self.game_info_url_1).content)['data']['mode'], 'pvp')

    def test_own_hero_get_cached_data(self):
        with mock.patch('game.heroes.prototypes.HeroPrototype.cached_ui_info', mock.Mock(return_value={})) as cached_ui_info:
            with mock.patch('game.heroes.prototypes.HeroPrototype.ui_info', mock.Mock(return_value={})) as ui_info:
                self.client.get(self.game_info_url_1)

        self.assertEqual(cached_ui_info.call_count, 1)
        self.assertEqual(cached_ui_info.call_args, mock.call(from_cache=True))
        self.assertEqual(ui_info.call_count, 0)

    def test_other_hero_get_not_cached_data(self):
        with mock.patch('game.heroes.prototypes.HeroPrototype.cached_ui_info') as cached_ui_info:
            with mock.patch('game.heroes.prototypes.HeroPrototype.ui_info', mock.Mock(return_value={})) as ui_info:
                self.client.get(self.game_info_url_2)

        self.assertEqual(cached_ui_info.call_count, 0)
        self.assertEqual(ui_info.call_count, 1)
        self.assertEqual(ui_info.call_args, mock.call(for_last_turn=True, quests_info=False))



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
