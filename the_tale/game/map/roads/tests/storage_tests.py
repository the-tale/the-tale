# coding: utf-8

from django.test import TestCase

from dext.settings import settings

from game.logic import create_test_map

from game.map.roads.models import Road
from game.map.roads.storage import RoadsStorage
from game.map.roads.exceptions import RoadsException

class RoadsStorageTest(TestCase):

    def setUp(self):
        self.p1, self.p2, self.p3 = create_test_map()
        self.storage = RoadsStorage()
        self.storage.sync()

    def test_initialization(self):
        storage = RoadsStorage()
        self.assertEqual(storage._data, {})
        self.assertEqual(storage._version, -1)

    def test_sync(self):
        self.assertEqual(len(self.storage._data), 2)
        self.assertEqual(self.storage._version,  0)

        road = Road.objects.order_by('?')[0]
        road.length = 666
        road.save()

        self.storage.sync()
        self.assertFalse(self.storage[road.id].length == 666)

        self.storage.sync(force=True)
        self.assertTrue(self.storage[road.id].length == 666)

    def test_sync_after_settings_update(self):
        self.assertEqual(len(self.storage._data), 2)
        self.assertEqual(self.storage._version, 0)

        road = Road.objects.order_by('?')[0]
        road.length = 666
        road.save()

        self.storage.sync()
        self.assertFalse(self.storage[road.id].length == 666)

        settings[self.storage.SETTINGS_KEY] = str(self.storage._version + 1)

        self.storage.sync()
        self.assertTrue(self.storage[road.id].length == 666)

    def test_getitem_wrong_id(self):
        self.assertRaises(RoadsException, self.storage.__getitem__, 666)

    def test_getitem(self):
        road = Road.objects.order_by('?')[0]
        self.assertEqual(self.storage[road.id].id, road.id)

    def test_get(self):
        road = Road.objects.order_by('?')[0]
        self.assertEqual(self.storage.get(666, self.storage[road.id]), self.storage[road.id])
        self.assertEqual(self.storage.get(road.id, 666).id, road.id)

    def test_all(self):
        self.assertEqual(len(self.storage.all()), 2)

    def test_contains(self):
        road = Road.objects.order_by('?')[0]
        self.assertTrue(road.id in self.storage)
        self.assertFalse(666 in self.storage)
