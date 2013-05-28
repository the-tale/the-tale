# coding: utf-8
import datetime
import jinja2

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase

from accounts.logic import register_user

from game.heroes.prototypes import HeroPrototype

from game.logic import create_test_map


class TestShowRequests(TestCase):

    def setUp(self):
        super(TestShowRequests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.client = client.Client()

    def test_wrong_place_id(self):
        self.check_html_ok(self.request_html(reverse('game:map:places:show', args=['wrong_id'])), texts=['places.place.wrong_format'])

    def test_place_does_not_exist(self):
        self.check_html_ok(self.request_html(reverse('game:map:places:show', args=[666])), texts=['places.place.not_found'], status_code=404)

    def test_no_heroes(self):
        texts = [('pgf-no-heroes-message', 1 + len(self.place_1.persons))]
        self.check_html_ok(self.request_html(reverse('game:map:places:show', args=[self.place_1.id])), texts=texts)

    def test_heroes(self):
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        hero_1 = HeroPrototype.get_by_account_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        hero_2 = HeroPrototype.get_by_account_id(account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        hero_3 = HeroPrototype.get_by_account_id(account_id)

        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_1.preferences.set_place_id(self.place_1.id)
        hero_1.preferences.set_friend_id(self.place_1.persons[0].id)
        hero_1.preferences.set_enemy_id(self.place_1.persons[-1].id)
        hero_1.save()

        hero_2.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_2.preferences.set_place_id(self.place_1.id)
        hero_2.preferences.set_friend_id(self.place_1.persons[-1].id)
        hero_2.preferences.set_enemy_id(self.place_1.persons[0].id)
        hero_2.save()

        hero_3.preferences.set_place_id(self.place_1.id)
        hero_3.preferences.set_friend_id(self.place_1.persons[-1].id)
        hero_3.preferences.set_enemy_id(self.place_1.persons[0].id)
        hero_3.save()

        texts = [(jinja2.escape(hero_1.name), 3),
                 (jinja2.escape(hero_2.name), 3),
                 (jinja2.escape(hero_3.name), 0)]

        self.check_html_ok(self.request_html(reverse('game:map:places:show', args=[self.place_1.id])), texts=texts)
