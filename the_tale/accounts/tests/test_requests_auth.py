# coding: utf-8
import time

from django.test import client

from dext.common.utils import s11n
from dext.common.utils.urls import url

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.logic import register_user, logout_url
from the_tale.accounts.conf import accounts_settings

from the_tale.game.logic import create_test_map


class AuthRequestsTests(TestCase):

    def setUp(self):
        super(AuthRequestsTests, self).setUp()
        create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account_id = account_id
        self.client = client.Client()

    def test_login_page(self):
        response = self.client.get(url('accounts:auth:page-login'))
        self.check_html_ok(response)

    def test_login_page_after_login(self):
        self.request_login('test_user@test.com')
        self.check_redirect(url('accounts:auth:page-login'), '/')

    def test_login_command(self):
        self.request_login('test_user@test.com', '111111', remember=False)
        self.assertTrue(self.client.session.get_expiry_age() < accounts_settings.SESSION_REMEMBER_TIME - 10)

    def test_login__remeber(self):
        self.request_login('test_user@test.com', '111111', remember=True)
        self.assertTrue(self.client.session.get_expiry_age() > accounts_settings.SESSION_REMEMBER_TIME - 10)

    def test_login(self):
        response = self.client.post(url('accounts:auth:api-login', api_version='1.0', api_client='test-1.0', next_url='/bla-bla'),
                                    {'email': 'test_user@test.com', 'password': '111111'})
        self.check_ajax_ok(response)

        data = s11n.from_json(response.content)

        self.assertEqual(data['data']['next_url'], '/bla-bla')
        self.assertEqual(data['data']['account_id'], self.account_id)
        self.assertEqual(data['data']['account_name'], 'test_user')
        self.assertTrue(data['data']['session_expire_at'] > time.time())

    def test_logout_command_post(self):
        self.request_logout()

    def test_logout_command_get(self):
        self.check_redirect(logout_url(), '/')
