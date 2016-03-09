# coding: utf-8
import mock
import random

from the_tale.common.utils import testcase

from the_tale.game import names

from the_tale.game.logic import create_test_map

from the_tale.game.map.conf import map_settings

from ..models import Building
from ..prototypes import BuildingPrototype, ResourceExchangePrototype
from .. import storage
from ..relations import RESOURCE_EXCHANGE_TYPE


class BuildingPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(BuildingPrototypeTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()


    def test_get_available_positions(self):

        building = BuildingPrototype.create(self.place_1.persons[0],
                                            utg_name=names.generator.get_test_name(name='building-name'))

        positions = BuildingPrototype.get_available_positions(self.place_1.x, self.place_1.y)

        self.assertTrue(positions)

        for place in storage.places.all():
            self.assertFalse((place.x, place.y) in positions)

        for building in storage.buildings.all():
            self.assertFalse((building.x, building.y) in positions)

        for x, y in positions:
            self.assertTrue(0 <= x < map_settings.WIDTH)
            self.assertTrue(0 <= y < map_settings.HEIGHT)


    def test_dynamic_position_radius(self):
        with mock.patch('the_tale.game.balance.constants.BUILDING_POSITION_RADIUS', 2):
            positions = BuildingPrototype.get_available_positions(-3, -1)
            self.assertEqual(positions, set([(0, 0), (0, 1), (0, 2)]))

        with mock.patch('the_tale.game.balance.constants.BUILDING_POSITION_RADIUS', 2):
            positions = BuildingPrototype.get_available_positions(-4, -1)
            self.assertEqual(positions, set([(0, 0), (0, 1), (0, 2), (0, 3)]))

    def test_create(self):
        self.assertEqual(Building.objects.all().count(), 0)

        old_version = storage.buildings.version

        name = names.generator.get_test_name(name='building-name')

        building = BuildingPrototype.create(self.place_1.persons[0], utg_name=name)

        self.assertNotEqual(old_version, storage.buildings.version)

        self.assertEqual(Building.objects.all().count(), 1)

        old_version = storage.buildings.version

        name_2 = names.generator.get_test_name(name='building-name-2')
        building_2 = BuildingPrototype.create(self.place_1.persons[0], utg_name=name_2)

        self.assertEqual(old_version, storage.buildings.version)
        self.assertEqual(Building.objects.all().count(), 1)
        self.assertEqual(hash(building), hash(building_2))
        self.assertEqual(building.utg_name, name)

    def test_create_after_destroy(self):
        self.assertEqual(Building.objects.all().count(), 0)

        old_version = storage.buildings.version

        person = self.place_1.persons[0]

        name = names.generator.get_test_name(name='building-name')
        building = BuildingPrototype.create(person, utg_name=name)
        building.destroy()

        name_2 = names.generator.get_test_name(name='building-name-2')
        building = BuildingPrototype.create(person, utg_name=name_2)

        self.assertNotEqual(old_version, storage.buildings.version)

        self.assertEqual(Building.objects.all().count(), 1)
        self.assertEqual(building.utg_name, name_2)

    def test_amortize(self):
        building = BuildingPrototype.create(self.place_1.persons[0], utg_name=names.generator.get_test_name(name='building-name'))

        old_integrity = building.integrity

        building.amortize(1000)

        self.assertTrue(old_integrity > building.integrity)

        building._model.integrity = -1

        building.amortize(1000)

        self.assertEqual(building.integrity, 0)
        self.assertTrue(building.state.is_WORKING)


    def test_amortization_grows(self):
        building = BuildingPrototype.create(self.place_1.persons[0], utg_name=names.generator.get_test_name(name='building-name'))

        old_integrity = building.integrity
        building.amortize(1000)
        amortization_delta = old_integrity - building.integrity

        building_2 = BuildingPrototype.create(self.place_1.persons[1], utg_name=names.generator.get_test_name(name='building-name-2'))

        old_integrity_2 = building_2.integrity
        building_2.amortize(1000)
        amortization_delta_2 = old_integrity_2 - building_2.integrity

        self.assertTrue(amortization_delta < amortization_delta_2)

    def test_amortization_delta_depends_from_person_building_amortization_speed(self):
        person = self.place_1.persons[0]
        building = BuildingPrototype.create(person, utg_name=names.generator.get_test_name(name='building-name'))

        person.attrs.building_amortization_speed = 1

        with self.check_decreased(lambda: building.amortization_delta(1000)):
            person.attrs.building_amortization_speed = 0.5


    def test_save__update_storage(self):
        building = BuildingPrototype.create(self.place_1.persons[0], utg_name=names.generator.get_test_name(name='building-name'))

        old_version = storage.buildings.version
        building.save()
        self.assertNotEqual(old_version, storage.buildings.version)


    def test_destroy__update_storage(self):
        building = BuildingPrototype.create(self.place_1.persons[0], utg_name=names.generator.get_test_name(name='building-name'))

        old_version = storage.buildings.version
        building.destroy()
        self.assertNotEqual(old_version, storage.buildings.version)
        self.assertFalse(building.id in storage.buildings)




class ResourceExchangeTests(testcase.TestCase):

    def setUp(self):
        super(ResourceExchangeTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.resource_1 = random.choice(RESOURCE_EXCHANGE_TYPE.records)
        self.resource_2 = random.choice(RESOURCE_EXCHANGE_TYPE.records)

        self.exchange = ResourceExchangePrototype.create(place_1=self.place_1,
                                                         place_2=self.place_2,
                                                         resource_1=self.resource_1,
                                                         resource_2=self.resource_2,
                                                         bill=None)

    def test_create(self):
        self.assertEqual(self.exchange.place_1.id, self.place_1.id)
        self.assertEqual(self.exchange.place_2.id, self.place_2.id)
        self.assertEqual(self.exchange.resource_1, self.resource_1)
        self.assertEqual(self.exchange.resource_2, self.resource_2)
        self.assertEqual(self.exchange.bill_id, None)

    def test_get_resources_for_place__place_1(self):
        self.assertEqual(self.exchange.get_resources_for_place(self.place_1),
                         (self.resource_1, self.resource_2, self.place_2))

    def test_get_resources_for_place__place_2(self):
        self.assertEqual(self.exchange.get_resources_for_place(self.place_2),
                         (self.resource_2, self.resource_1, self.place_1))


    def test_get_resources_for_place__wrong_place(self):
        self.assertEqual(self.exchange.get_resources_for_place(self.place_3),
                         (RESOURCE_EXCHANGE_TYPE.NONE, RESOURCE_EXCHANGE_TYPE.NONE, None))
