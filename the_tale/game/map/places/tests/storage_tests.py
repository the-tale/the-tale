# coding: utf-8
import uuid

from django.test import TestCase

from dext.settings import settings

from game.logic import create_test_map

from game.map.places.models import Place
from game.map.places.storage import PlacesStorage
from game.map.places.exceptions import PlacesException

class PlacesStorageTest(TestCase):

    def setUp(self):
        self.p1, self.p2, self.p3 = create_test_map()
        self.storage = PlacesStorage()
        self.storage.sync()

    def test_initialization(self):
        storage = PlacesStorage()
        self.assertEqual(storage._data, {})
        self.assertEqual(storage._version, None)

    def test_sync(self):
        self.assertEqual(len(self.storage._data), 3)
        self.assertTrue(self.storage._version > 0)

        place = Place.objects.get(id=self.p1.id)
        place.name = '!!!'
        place.save()

        self.storage.sync()
        self.assertFalse(self.storage[self.p1.id].name == '!!!')

        self.storage.sync(force=True)
        self.assertTrue(self.storage[self.p1.id].name == '!!!')

    def test_sync_after_settings_update(self):
        self.assertEqual(len(self.storage._data), 3)
        self.assertTrue(self.storage._version > 0)

        place = Place.objects.get(id=self.p1.id)
        place.name = '!!!'
        place.save()

        self.storage.sync()
        self.assertFalse(self.storage[self.p1.id].name == '!!!')

        settings[self.storage.SETTINGS_KEY] = uuid.uuid4().hex

        self.storage.sync()
        self.assertTrue(self.storage[self.p1.id].name == '!!!')


    def test_getitem_wrong_id(self):
        self.assertRaises(PlacesException, self.storage.__getitem__, 666)

    def test_getitem(self):
        self.assertEqual(self.storage[self.p1.id].id, self.p1.id)

    def test_get(self):
        self.assertEqual(self.storage.get(666, self.p2).id, self.p2.id)
        self.assertEqual(self.storage.get(self.p3.id, self.p1).id, self.p3.id)

    def test_all(self):
        self.assertEqual(len(self.storage.all()), 3)

    def test_random_place(self):
        places = set([self.p1.id, self.p2.id, self.p3.id])

        for i in xrange(100):
            places.discard(self.storage.random_place().id)

        self.assertFalse(places)

    def test_contains(self):
        self.assertTrue(self.p1.id in self.storage)
        self.assertFalse(666 in self.storage)
