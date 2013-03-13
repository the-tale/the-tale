# coding: utf-8
from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase

from accounts.logic import register_user

from game.logic import create_test_map

class AuthRequestsTests(TestCase):

    def setUp(self):
        super(AuthRequestsTests, self).setUp()
        create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')
        self.client = client.Client()

    def test_login_page(self):
        response = self.client.get(reverse('accounts:auth:login'))
        self.check_html_ok(response)

    def test_login_page_after_login(self):
        self.request_login('test_user@test.com')
        self.check_redirect(reverse('accounts:auth:login'), '/')

    def test_login_command(self):
        self.request_login('test_user@test.com', '111111')

    def test_logout_command_post(self):
        self.request_logout()

    def test_logout_command_get(self):
        self.check_redirect(reverse('accounts:auth:logout'), '/')
