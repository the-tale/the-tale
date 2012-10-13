# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase

from game.logic import create_test_bundle, create_test_map

class HeroRequestsTest(TestCase):

    def setUp(self):
        create_test_map()

        self.bundle = create_test_bundle('test_user')
        self.action_idl = self.bundle.tests_get_last_action()
        self.hero = self.bundle.tests_get_hero()

        self.client = client.Client()
        self.client.post(reverse('accounts:login'), {'email': 'test_user@test.com', 'password': '111111'})

    def test_index(self):
        response = self.client.get(reverse('game:heroes:'))
        self.assertRedirects(response, '/', status_code=302, target_status_code=200)

    def test_wrong_hero_id(self):
        self.check_html_ok(self.client.get(reverse('game:heroes:show', args=['dsdsd'])), texts=[('heroes.wrong_hero_id', 1)], status_code=404)
