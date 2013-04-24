# coding: utf-8
import mock

from common.utils import testcase

from accounts.logic import register_user

from game.balance.enums import RACE

from game.prototypes import TimePrototype
from game.logic import create_test_map
from game.heroes.prototypes import HeroPrototype

from game.map.conf import map_settings

from game.map.places.models import Building
from game.map.places.prototypes import BuildingPrototype
from game.map.places.storage import places_storage, buildings_storage


class PlacePrototypeTests(testcase.TestCase):

    def setUp(self):
        super(PlacePrototypeTests, self).setUp()
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

    def test_update_heroes_number(self):
        self.hero_1.preferences.place_id = self.p1.id
        self.hero_1.save()

        self.hero_2.preferences.place_id = self.p1.id
        self.hero_2.save()

        self.hero_2.preferences.place_id = self.p1.id
        self.hero_2.save()

        result, account_id, bundle_id = register_user('test_user_4') # fast_account
        hero_4 = HeroPrototype.get_by_account_id(account_id)
        hero_4.preferences.place_id = self.p1.id
        hero_4.save()

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



class BuildingPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(BuildingPrototypeTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()


    def test_get_available_positions(self):

        building = BuildingPrototype.create(self.place_1.persons[0])

        positions = BuildingPrototype.get_available_positions(self.place_1.x, self.place_1.y)

        self.assertTrue(positions)

        for place in places_storage.all():
            self.assertFalse((place.x, place.y) in positions)

        for building in buildings_storage.all():
            self.assertFalse((building.x, building.y) in positions)

        for x, y in positions:
            self.assertTrue(0 <= x < map_settings.WIDTH)
            self.assertTrue(0 <= y < map_settings.HEIGHT)


    def test_dynamic_position_radius(self):
        with mock.patch('game.map.places.conf.places_settings.BUILDING_POSITION_RADIUS', 2):
            positions = BuildingPrototype.get_available_positions(-3, -1)
            self.assertEqual(positions, set([(0, 0), (0, 1), (0, 2)]))

        with mock.patch('game.map.places.conf.places_settings.BUILDING_POSITION_RADIUS', 2):
            positions = BuildingPrototype.get_available_positions(-4, -1)
            self.assertEqual(positions, set([(0, 0), (0, 1), (0, 2), (0, 3)]))

    def test_create(self):
        self.assertEqual(Building.objects.all().count(), 0)

        old_version = buildings_storage.version

        building = BuildingPrototype.create(self.place_1.persons[0])

        self.assertNotEqual(old_version, buildings_storage.version)

        self.assertEqual(Building.objects.all().count(), 1)

        old_version = buildings_storage.version

        building_2 = BuildingPrototype.create(self.place_1.persons[0])

        self.assertEqual(old_version, buildings_storage.version)
        self.assertEqual(Building.objects.all().count(), 1)
        self.assertEqual(hash(building), hash(building_2))

    def test_amortize(self):
        building = BuildingPrototype.create(self.place_1.persons[0])

        old_integrity = building.integrity

        building.amortize(1000)

        self.assertTrue(old_integrity > building.integrity)

        building._model.integrity = 0

        building.amortize(1000)

        self.assertTrue(building.state._is_DESTROYED)


    def test_amortization_grows(self):
        building = BuildingPrototype.create(self.place_1.persons[0])

        old_integrity = building.integrity
        building.amortize(1000)
        amortization_delta = old_integrity - building.integrity

        building_2 = BuildingPrototype.create(self.place_1.persons[1])

        old_integrity_2 = building_2.integrity
        building_2.amortize(1000)
        amortization_delta_2 = old_integrity_2 - building_2.integrity

        self.assertTrue(amortization_delta < amortization_delta_2)

    def test_save__update_storage(self):
        building = BuildingPrototype.create(self.place_1.persons[0])

        old_version = buildings_storage.version
        building.save()
        self.assertNotEqual(old_version, buildings_storage.version)


    def test_destroy__update_storage(self):
        building = BuildingPrototype.create(self.place_1.persons[0])

        old_version = buildings_storage.version
        building.destroy()
        self.assertNotEqual(old_version, buildings_storage.version)
        self.assertFalse(building.id in buildings_storage)
