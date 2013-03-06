# coding: utf-8
import mock

from common.utils import testcase

from accounts.logic import register_user

from game.balance.enums import RACE

from game.prototypes import TimePrototype
from game.logic import create_test_map
from game.heroes.prototypes import HeroPrototype


class PrototypeTests(testcase.TestCase):

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

    def test_sync_race_no_signal_when_race_not_changed(self):
        with mock.patch('game.map.places.signals.place_race_changed.send') as signal_counter:
            self.p1.sync_race()

        self.assertEqual(signal_counter.call_count, 0)

    def test_sync_race_signal_when_race_changed(self):
        for race in RACE._ALL:
            if self.p1.race != race:
                self.p1.race = race
                self.p1.save()
                break

        with mock.patch('game.map.places.signals.place_race_changed.send') as signal_counter:
            self.p1.sync_race()

        self.assertEqual(signal_counter.call_count, 1)
