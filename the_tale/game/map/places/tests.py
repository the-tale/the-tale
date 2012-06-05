# coding: utf-8

from django.test import TestCase

from game.map.places.prototypes import get_place_by_model
from game.map.places.models import Place, TERRAIN, PLACE_TYPE
from game.map.places.conf import places_settings
from game.map.places.exceptions import PlacesException

class PlacePowerTest(TestCase):

    def setUp(self):
        self.model = Place.objects.create(x=0,
                                          y=0,
                                          name='power_test_place',
                                          terrain=TERRAIN.GRASS,
                                          type=PLACE_TYPE.CITY,
                                          subtype='UNDEFINED',
                                          size=5 )

        self.place = get_place_by_model(self.model)
        self.place.sync_persons()


    def test_initialization(self):
        self.assertEqual(self.place.power, 0)

    def test_push_power(self):
        self.place.push_power(0, 10)
        self.assertEqual(self.place.power, 10)

        self.place.push_power(1, 1)
        self.assertEqual(self.place.power, 11)

        self.place.push_power(places_settings.POWER_HISTORY_LENGTH-1, 100)
        self.assertEqual(self.place.power, 111)

        self.place.push_power(places_settings.POWER_HISTORY_LENGTH, 1000)
        self.assertEqual(self.place.power, 1111)

        self.place.push_power(places_settings.POWER_HISTORY_LENGTH+1, 10000)
        self.assertEqual(self.place.power, 11101)

        self.place.push_power(places_settings.POWER_HISTORY_LENGTH+2, 100000)
        self.assertEqual(self.place.power, 111100)

    def test_push_power_exceptions(self):
        self.place.push_power(666, 10)
        self.assertRaises(PlacesException, self.place.push_power, 13, 1)

    def test_sync_power(self):
        persons = [person.id for person in self.place.persons]

        # we expected to have 3 persons, if it's wrong, see places_settings.SIZE_TO_PERSONS_NUMBER
        self.assertEqual(len(persons), 3)

        wrong_person_id = 666
        self.assertTrue(wrong_person_id not in persons)

        self.place.sync_power(0, {persons[1]: 1,
                                  persons[2]: 10 })
        self.assertEqual(self.place.power, 11)

        self.place.sync_power(1, {persons[1]: 100,
                                  persons[2]: 1000,
                                  wrong_person_id: 1})
        self.assertEqual(self.place.power, 1111)

        self.place.sync_power(2, {wrong_person_id: 1})
        self.assertEqual(self.place.power, 1111)

        self.place.sync_power(3, {})
        self.assertEqual(self.place.power, 1111)

        self.place.sync_power(places_settings.POWER_HISTORY_LENGTH-1, {persons[0]: 10000,
                                                                       persons[2]: 100000})
        self.assertEqual(self.place.power, 111111)

        self.place.sync_power(places_settings.POWER_HISTORY_LENGTH, {persons[0]: 1000000})
        self.assertEqual(self.place.power, 1111111)

        self.place.sync_power(places_settings.POWER_HISTORY_LENGTH+1, {persons[0]: 10000,
                                                                       persons[2]: 100000})
        self.assertEqual(self.place.power, 1221100)

    def test_sync_power_exception(self):
        persons = [person.id for person in self.place.persons]

        # we expected to have 3 persons, if it's wrong, see places_settings.SIZE_TO_PERSONS_NUMBER
        self.assertEqual(len(persons), 3)

        self.place.sync_power(666, {persons[1]: 1,
                                    persons[2]: 10 })
        self.assertRaises(PlacesException, self.place.sync_power, 13, {persons[1]: 100})
