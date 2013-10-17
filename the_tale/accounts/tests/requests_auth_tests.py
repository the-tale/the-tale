# coding: utf-8
from django.test import client

from dext.utils.urls import url

from common.utils.testcase import TestCase

from accounts.logic import register_user, logout_url
from accounts.conf import accounts_settings

from game.logic import create_test_map


class AuthRequestsTests(TestCase):

    def setUp(self):
        super(AuthRequestsTests, self).setUp()
        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')
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

    def test_logout_command_post(self):
        self.request_logout()

    def test_logout_command_get(self):
        self.check_redirect(logout_url(), '/')
