# coding: utf-8
import mock

from django.test import client
from django.core.urlresolvers import reverse

from dext.utils import s11n

from common.utils.testcase import TestCase
from common.postponed_tasks import PostponedTask, PostponedTaskPrototype

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, login_url

from game.logic import create_test_map
from game.pvp.models import BATTLE_1X1_STATE

from game.pvp.tests.helpers import PvPTestsMixin

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

    def test_login_required(self):
        self.check_redirect(reverse('game:pvp:'), login_url(reverse('game:pvp:')))

    def test_game_page_when_pvp_in_queue(self):
        self.pvp_create_battle(self.account_1, None)
        self.pvp_create_battle(self.account_2, None)
        self.request_login('test_user@test.com')
        self.check_redirect(reverse('game:pvp:'), reverse('game:'))

    def test_game_page_when_pvp_prepairing(self):
        self.pvp_create_battle(self.account_1, self.account_2)
        self.pvp_create_battle(self.account_2, self.account_1)
        self.request_login('test_user@test.com')
        self.check_html_ok(self.client.get(reverse('game:pvp:')), texts=[('pgf-change-name-warning', 1)])

    def test_game_page_when_pvp_processing(self):
        self.pvp_create_battle(self.account_1, self.account_2, BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, BATTLE_1X1_STATE.PROCESSING)
        self.request_login('test_user@test.com')
        self.check_html_ok(self.client.get(reverse('game:pvp:')), texts=[('pgf-change-name-warning', 1)])

    @mock.patch('game.heroes.prototypes.HeroPrototype.is_name_changed', True)
    def test_game_page_when_pvp_processing_change_name_warning_hiden(self):
        self.pvp_create_battle(self.account_1, self.account_2, BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, BATTLE_1X1_STATE.PROCESSING)
        self.request_login('test_user@test.com')
        self.check_html_ok(self.client.get(reverse('game:pvp:')), texts=[('pgf-change-name-warning', 0)])

    def test_game_info_when_pvp_in_queue(self):
        self.pvp_create_battle(self.account_1, None)
        self.pvp_create_battle(self.account_2, None)
        self.request_login('test_user@test.com')
        self.assertEqual(s11n.from_json(self.client.get(reverse('game:pvp:info')).content)['data']['mode'], 'pve')

    def test_game_info_when_pvp_prepairing(self):
        self.pvp_create_battle(self.account_1, self.account_2)
        self.pvp_create_battle(self.account_2, self.account_1)
        self.request_login('test_user@test.com')
        self.assertEqual(s11n.from_json(self.client.get(reverse('game:pvp:info')).content)['data']['mode'], 'pvp')

    def test_game_info_when_pvp_processing(self):
        self.pvp_create_battle(self.account_1, self.account_2, BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, BATTLE_1X1_STATE.PROCESSING)
        self.request_login('test_user@test.com')
        self.assertEqual(s11n.from_json(self.client.get(reverse('game:pvp:info')).content)['data']['mode'], 'pvp')

    def test_say_no_battle(self):
        self.request_login('test_user@test.com')
        self.check_ajax_error(self.client.post(reverse('game:pvp:say'), {'text': u'some text'}), 'pvp.say.no_battle')

    def test_say_battle_not_in_processing_state(self):
        self.request_login('test_user@test.com')
        self.pvp_create_battle(self.account_1, None)
        self.check_ajax_error(self.client.post(reverse('game:pvp:say'), {'text': u'some text'}), 'pvp.say.no_battle')

    def test_say_form_errors(self):
        self.request_login('test_user@test.com')
        self.pvp_create_battle(self.account_1, self.account_2, BATTLE_1X1_STATE.PROCESSING)
        self.check_ajax_error(self.client.post(reverse('game:pvp:say'), {'text': u''}), 'pvp.say.form_errors')

    def test_say_success(self):
        self.request_login('test_user@test.com')
        self.pvp_create_battle(self.account_1, self.account_2, BATTLE_1X1_STATE.PROCESSING)
        response = self.client.post(reverse('game:pvp:say'), {'text': u'some text'})
        task = PostponedTaskPrototype(PostponedTask.objects.all()[0])
        self.check_ajax_processing(response, task.status_url)
