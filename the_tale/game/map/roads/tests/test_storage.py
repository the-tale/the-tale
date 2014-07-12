# coding: utf-8
import uuid

from the_tale.common.utils import testcase

from dext.settings import settings

from the_tale.game.logic import create_test_map

from the_tale.game.map.roads.models import Road
from the_tale.game.map.roads.storage import RoadsStorage
from the_tale.game.map.roads import exceptions

class RoadsStorageTest(testcase.TestCase):

    def setUp(self):
        super(RoadsStorageTest, self).setUp()
        self.p1, self.p2, self.p3 = create_test_map()
        self.storage = RoadsStorage()
        self.storage.sync()

    def test_initialization(self):
        storage = RoadsStorage()
        self.assertEqual(storage._data, {})
        self.assertEqual(storage._version, None)

    def test_sync(self):
        self.assertEqual(len(self.storage._data), 2)

        road = Road.objects.order_by('?')[0]
        road.length = 666
        road.save()

        self.storage.sync()
        self.assertFalse(self.storage[road.id].length == 666)

        self.storage.sync(force=True)
        self.assertTrue(self.storage[road.id].length == 666)

    def test_sync_after_settings_update(self):
        self.assertEqual(len(self.storage._data), 2)

        road = Road.objects.order_by('?')[0]
        road.length = 666
        road.save()

        self.storage.sync()
        self.assertFalse(self.storage[road.id].length == 666)

        settings[self.storage.SETTINGS_KEY] = uuid.uuid4().hex

        self.storage.sync()
        self.assertTrue(self.storage[road.id].length == 666)

    def test_getitem_wrong_id(self):
        self.assertRaises(exceptions.RoadsStorageError, self.storage.__getitem__, 666)

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
