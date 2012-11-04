# coding: utf-8
from django.test import TestCase

from accounts.logic import register_user

from game.prototypes import TimePrototype
from game.logic import create_test_map
from game.heroes.prototypes import HeroPrototype

class PrototypeTests(TestCase):

    def setUp(self):
        self.p1, self.p2, self.p3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.hero_1 = HeroPrototype.get_by_account_id(account_id)

        result, account_id, bundle_id = register_user('test_user2', 'test_user2@test.com', '111111')
        self.hero_2 = HeroPrototype.get_by_account_id(account_id)

        result, account_id, bundle_id = register_user('test_user3', 'test_user3@test.com', '111111')
        self.hero_3 = HeroPrototype.get_by_account_id(account_id)

        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()

        self.hero_1.mark_as_active()
        self.hero_2.mark_as_active()


    def test_initialize(self):
        self.assertEqual(self.p1.heroes_number, 0)

    def test_update_friends_number(self):
        self.hero_1.preferences.place_id = self.p1.id
        self.hero_1.save()

        self.hero_2.preferences.place_id = self.p1.id
        self.hero_2.save()

        self.hero_2.preferences.place_id = self.p1.id
        self.hero_2.save()

        self.p1.update_heroes_number()

        self.assertEqual(self.p1.heroes_number, 2)
