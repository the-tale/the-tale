# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase

from game.logic import create_test_map
from accounts.logic import register_user

class TestPlaceRequests(TestCase):

    def setUp(self):
        self.place_1, self.place_2, self.place_3 = create_test_map()
        register_user('test_user', 'test_user@test.com', '111111')
        self.client = client.Client()

    def test_place_info_anonimouse(self):
        response = self.client.get(reverse('game:map:places:map-info', args=[self.place_1.id]))
        self.assertEqual(response.status_code, 200)

    def test_place_info_logined(self):
        self.request_login('test_user@test.com')
        response = self.client.get(reverse('game:map:places:map-info', args=[self.place_1.id]))
        self.assertEqual(response.status_code, 200)
