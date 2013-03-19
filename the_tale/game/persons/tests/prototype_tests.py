# coding: utf-8
import mock
import datetime

from common.utils import testcase

from accounts.logic import register_user

from game.prototypes import TimePrototype
from game.logic import create_test_map
from game.heroes.prototypes import HeroPrototype

from game.map.places.prototypes import BuildingPrototype

from game.persons.models import PERSON_STATE
from game.persons.tests.helpers import create_person

class PrototypeTests(testcase.TestCase):

    def setUp(self):
        super(PrototypeTests, self).setUp()
        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()

        self.p1, self.p2, self.p3 = create_test_map()

        self.person = create_person(self.p1, PERSON_STATE.IN_GAME)

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
        self.assertEqual(self.person.friends_number, 0)
        self.assertEqual(self.person.enemies_number, 0)
        self.assertEqual(self.person.created_at_turn, TimePrototype.get_current_turn_number() - 1)
        self.assertTrue(self.person.is_stable)

    @mock.patch('game.persons.conf.persons_settings.POWER_STABILITY_PERCENT', 1.0)
    @mock.patch('game.persons.conf.persons_settings.POWER_STABILITY_WEEKS', -1.0)
    def test_is_stable_no_time_delay_no_percent(self):
        self.assertFalse(self.person.is_stable)

    @mock.patch('game.persons.conf.persons_settings.POWER_STABILITY_PERCENT', 1.0)
    @mock.patch('game.persons.conf.persons_settings.POWER_STABILITY_WEEKS', 10.0)
    def test_is_stable_with_time_delay(self):
        self.assertTrue(self.person.is_stable)

    @mock.patch('game.persons.conf.persons_settings.POWER_STABILITY_PERCENT', -1.0)
    @mock.patch('game.persons.conf.persons_settings.POWER_STABILITY_WEEKS', -1.0)
    def test_is_stable_with_percent(self):
        self.assertTrue(self.person.is_stable)

    def test_update_friends_number(self):
        self.hero_1.preferences.friend_id = self.person.id
        self.hero_1.save()

        self.hero_2.preferences.friend_id = self.person.id
        self.hero_2.save()

        self.hero_2.preferences.friend_id = self.person.id
        self.hero_2.save()

        self.person.update_friends_number()
        self.person.update_enemies_number()

        self.assertEqual(self.person.friends_number, 2)
        self.assertEqual(self.person.enemies_number, 0)

    def test_update_enemies_number(self):
        self.hero_1.preferences.enemy_id = self.person.id
        self.hero_1.save()

        self.hero_2.preferences.enemy_id = self.person.id
        self.hero_2.save()

        self.hero_2.preferences.enemy_id = self.person.id
        self.hero_2.save()

        self.person.update_friends_number()
        self.person.update_enemies_number()

        self.assertEqual(self.person.friends_number, 0)
        self.assertEqual(self.person.enemies_number, 2)

    def test_move_out_game(self):
        current_time = datetime.datetime.now()
        self.assertTrue(self.person.out_game_at < current_time)
        self.assertEqual(self.person.state, PERSON_STATE.IN_GAME)
        self.person.move_out_game()
        self.assertTrue(self.person.out_game_at > current_time)
        self.assertEqual(self.person.state, PERSON_STATE.OUT_GAME)

    def test_move_out_game_with_building(self):
        building = BuildingPrototype.create(self.person)
        self.assertTrue(building.state._is_WORKING)
        self.person.move_out_game()
        self.assertTrue(building.state._is_DESTROYED)

    def test_mastery_from_building(self):

        while True:
            person = create_person(self.p1, PERSON_STATE.IN_GAME)
            old_mastery = person.mastery

            if old_mastery < 0.8:
                break

        building = BuildingPrototype.create(person)

        max_mastery = person.mastery

        building._model.integrity = 0.5

        self.assertTrue(old_mastery < person.mastery < max_mastery)

    def test_power_from_building(self):

        with mock.patch('game.workers.highlevel.Worker.cmd_change_person_power') as change_person_power_call:
            self.person.cmd_change_power(100)

        self.assertEqual(change_person_power_call.call_args, mock.call(self.person.id, 100))

        BuildingPrototype.create(self.person)

        with mock.patch('game.workers.highlevel.Worker.cmd_change_person_power') as change_person_power_call:
            self.person.cmd_change_power(100)

        self.assertTrue(change_person_power_call.call_args[0][1] > 100)
