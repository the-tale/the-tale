# coding: utf-8

from django.test import TestCase

from game.map.places.prototypes import PlacePrototype
from game.map.places.models import Place, TERRAIN, PLACE_TYPE
from game.map.places.conf import places_settings
from game.map.places.exceptions import PlacesException

from game.map.places.storage import places_storage
from game.persons.storage import persons_storage

class PlacePowerTest(TestCase):

    def setUp(self):
        places_storage.clear()
        persons_storage.clear()

        self.model = Place.objects.create(x=0,
                                          y=0,
                                          name='power_test_place',
                                          terrain=TERRAIN.GRASS,
                                          type=PLACE_TYPE.CITY,
                                          subtype='UNDEFINED',
                                          size=5 )

        self.place = PlacePrototype(self.model)
        self.place.sync_persons()

        places_storage.sync(force=True)
        persons_storage.sync(force=True)


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
