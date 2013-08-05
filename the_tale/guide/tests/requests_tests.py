# coding: utf-8

from django.core.urlresolvers import reverse
from django.test import client

from dext.utils.urls import url

from common.utils.testcase import TestCase


class TestRequests(TestCase):

    def setUp(self):
        super(TestRequests, self).setUp()
        self.client = client.Client()

    def test_index(self):
        self.check_redirect(reverse('guide:'), reverse('guide:game'))

    def test_registration(self):
        self.check_html_ok(self.client.get(reverse('guide:registration')))

    def test_account_types(self):
        self.check_html_ok(self.client.get(reverse('guide:account-types')))

    def test_behavior_rules(self):
        self.check_html_ok(self.client.get(reverse('guide:behavior-rules')))

    def test_user_agreement(self):
        self.check_html_ok(self.client.get(reverse('guide:user-agreement')))

    def test_payments(self):
        self.check_html_ok(self.client.get(reverse('guide:payments')))

    def test_game(self):
        self.check_html_ok(self.client.get(reverse('guide:game')))

    def test_might(self):
        self.check_html_ok(self.client.get(reverse('guide:might')))

    def test_persons(self):
        self.check_html_ok(self.client.get(reverse('guide:persons')))

    def test_cities(self):
        self.check_html_ok(self.client.get(reverse('guide:cities')))

    def test_map(self):
        self.check_html_ok(self.client.get(reverse('guide:map')))

    def test_politics(self):
        self.check_html_ok(self.client.get(reverse('guide:politics')))

    def test_hero_abilities(self):
        from game.heroes.habilities import ABILITY_TYPE, ABILITY_ACTIVATION_TYPE, ABILITY_AVAILABILITY

        for ability_type in [None] + list(ABILITY_TYPE._records):
            for activation_type in [None] + list(ABILITY_ACTIVATION_TYPE._records):
                for availability in ABILITY_AVAILABILITY._records:
                    args = {'availability': availability.value}
                    if ability_type is not None:
                        args['ability_type'] = ability_type.value
                    if activation_type is not None:
                        args['activation_type'] = activation_type.value
                    self.check_html_ok(self.request_html(url('guide:hero-abilities', **args)),
                                       texts=(('guide.hero_abilities.activation_type.wrong_format', 0),
                                              ('guide.hero_abilities.ability_type.wrong_format', 0),
                                              ('guide.hero_abilities.availability.wrong_format', 0),))

    def test_hero_preferences(self):
        self.check_html_ok(self.client.get(reverse('guide:hero-preferences')))

    def test_pvp(self):
        self.check_html_ok(self.client.get(reverse('guide:pvp')))
