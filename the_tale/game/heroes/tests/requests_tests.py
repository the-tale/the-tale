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


class HeroPageRequestsTests(HeroRequestsTest):

    def setUp(self):
        super(HeroPageRequestsTests, self).setUp()

    def test_wrong_hero_id(self):
        self.check_html_ok(self.client.get(reverse('game:heroes:show', args=['dsdsd'])), texts=[('heroes.wrong_hero_id', 1)], status_code=404)

    def test_own_hero_page(self):
        self.check_html_ok(self.client.get(reverse('game:heroes:show', args=[self.hero.id])),
                           texts=(('pgf-health-percents', 1),
                                  ('pgf-experience-percents', 1),
                                  ('pgf-energy-percents', 1),
                                  ('pgf-power value', 1),
                                  ('pgf-money', 1),
                                  ('"pgf-health"', 1),
                                  ('pgf-max-health', 1),
                                  ('pgf-choose-ability-button', 1),
                                  ('pgf-choose-preference-button', 2),
                                  ('pgf-free-destiny-points', 1))) # in script and in 1 lvl preference


    def test_other_hero_page(self):
        texts = (('pgf-health-percents', 0),
                                  ('pgf-experience-percents', 0),
                                  ('pgf-energy-percents', 0),
                                  ('pgf-power value', 1),
                                  ('pgf-money', 0),
                                  ('"pgf-health"', 0),
                                  ('pgf-max-health', 1),
                                  ('pgf-choose-ability-button', 0),
                                  ('pgf-choose-preference-button', 0),
                                  ('pgf-free-destiny-points', 0))

        self.client.post(reverse('accounts:logout'))
        self.check_html_ok(self.client.get(reverse('game:heroes:show', args=[self.hero.id])), texts=texts)

        create_test_bundle('test_user_2')

        self.client.post(reverse('accounts:login'), {'email': 'test_user_2@test.com', 'password': '111111'})
        self.check_html_ok(self.client.get(reverse('game:heroes:show', args=[self.hero.id])), texts=texts)
