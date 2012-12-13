# coding: utf-8

from django.core.urlresolvers import reverse
from django.test import client

from common.utils.testcase import TestCase


class TestRequests(TestCase):

    def setUp(self):
        self.client = client.Client()

    def test_index(self):
        self.check_redirect(reverse('guide:'), reverse('guide:game'))

    def test_registration(self):
        self.check_html_ok(self.client.get(reverse('guide:registration')))

    def test_game(self):
        self.check_html_ok(self.client.get(reverse('guide:game')))

    def test_might(self):
        self.check_html_ok(self.client.get(reverse('guide:might')))

    def test_cities(self):
        self.check_html_ok(self.client.get(reverse('guide:cities')))

    def test_map(self):
        self.check_html_ok(self.client.get(reverse('guide:map')))

    def test_politics(self):
        self.check_html_ok(self.client.get(reverse('guide:politics')))

    def test_hero_abilities(self):
        self.check_html_ok(self.client.get(reverse('guide:hero-abilities')))

    def test_hero_preferences(self):
        self.check_html_ok(self.client.get(reverse('guide:hero-preferences')))
