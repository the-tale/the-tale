# coding: utf-8
# coding: utf-8
from django.test import TestCase, client
from django.core.urlresolvers import reverse


class TestRequests(TestCase):

    def setUp(self):
        self.client = client.Client()

    def test_registration(self):
        response = self.client.get(reverse('guide:registration'))
        self.assertEqual(response.status_code, 200)

    def test_game(self):
        response = self.client.get(reverse('guide:game'))
        self.assertEqual(response.status_code, 200)

    def test_hero_abilities(self):
        response = self.client.get(reverse('guide:hero-abilities'))
        self.assertEqual(response.status_code, 200)
