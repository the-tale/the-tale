# coding: utf-8
import datetime

import mock

from django.test import client
from django.core.urlresolvers import reverse

from dext.common.utils import s11n

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user, login_page_url

from the_tale.game.logic import create_test_map, game_info_url

from the_tale.game.pvp.models import BATTLE_1X1_STATE
from the_tale.game.pvp.tests.helpers import PvPTestsMixin

from the_tale.cms.news import logic as news_logic


class RequestTestsBase(TestCase, PvPTestsMixin):

    def setUp(self):
        super(RequestTestsBase, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account_1_id = account_id
        self.account_1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2_id = account_id
        self.account_2 = AccountPrototype.get_by_id(account_id)

        self.client = client.Client()

        self.game_info_url_1 = game_info_url(account_id=self.account_1.id)
        self.game_info_url_2 = game_info_url(account_id=self.account_2.id)
        self.game_info_url_no_id = game_info_url()

        self.request_login('test_user@test.com')

class GamePageRequestTests(RequestTestsBase):

    def test_game_page_unlogined(self):
        self.request_logout()
        self.check_redirect(reverse('game:'), login_page_url(reverse('game:')))

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
        self.check_ajax_ok(self.request_ajax_json(self.game_info_url_1))

    def test_logined(self):
        response = self.client.get(self.game_info_url_1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(s11n.from_json(response.content)['data'].keys()), set(('turn', 'mode', 'map_version', 'account', 'enemy', 'game_state')))

    def test_no_id__logined(self):
        with mock.patch('the_tale.game.logic.form_game_info', mock.Mock(return_value={})) as form_game_info:
            self.check_ajax_ok(self.client.get(self.game_info_url_no_id))

        self.assertEqual(form_game_info.call_count, 1)
        self.assertEqual(form_game_info.call_args_list[0][1]['account'].id, self.account_1.id)

    def test_no_id__unlogined(self):
        self.request_logout()

        with mock.patch('the_tale.game.logic.form_game_info', mock.Mock(return_value={})) as form_game_info:
            self.check_ajax_ok(self.client.get(self.game_info_url_no_id))

        self.assertEqual(form_game_info.call_count, 1)
        self.assertEqual(form_game_info.call_args_list[0][1]['account'], None)

    def test_account_not_exists(self):
        response = self.request_ajax_json(game_info_url(account_id=666))
        self.check_ajax_error(response, 'account.wrong_value')

    def test_wrong_account_id(self):
        response = self.request_ajax_json(game_info_url(account_id='sdsd'))
        self.check_ajax_error(response, 'account.wrong_format')

    def test_client_turns(self):
        self.check_ajax_error(self.request_ajax_json(game_info_url(client_turns=['dds'])), 'client_turns.wrong_format')
        self.check_ajax_error(self.request_ajax_json(game_info_url(client_turns=['1', ''])), 'client_turns.wrong_format')
        self.check_ajax_ok(self.request_ajax_json(game_info_url(client_turns=['1'])))
        self.check_ajax_ok(self.request_ajax_json(game_info_url(client_turns=['1, 2, 3 ,4'])))
        self.check_ajax_ok(self.request_ajax_json(game_info_url(client_turns=[1, 2, 3 ,4])))
        self.check_ajax_ok(self.request_ajax_json(game_info_url(client_turns=['1',' 2',' 3 ','4'])))

    def test_client_turns_passed_to_data_receiver(self):
        with mock.patch('the_tale.game.heroes.objects.Hero.cached_ui_info_for_hero',
                        mock.Mock(return_value={'actual_on_turn': 666})) as cached_ui_info_for_hero:
            self.check_ajax_ok(self.request_ajax_json(game_info_url(client_turns=[1, 2, 3 ,4])))

        self.assertEqual(cached_ui_info_for_hero.call_args_list,
                         [mock.call(account_id=self.account_1.id,
                                    recache_if_required=True,
                                    patch_turns=[1, 2, 3, 4],
                                    for_last_turn=False)])



class NewsAlertsTests(TestCase):

    def setUp(self):
        super(NewsAlertsTests, self).setUp()
        create_test_map()
        self.client = client.Client()

        self.news = news_logic.create_news(caption='news-caption', description='news-description', content='news-content')

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
