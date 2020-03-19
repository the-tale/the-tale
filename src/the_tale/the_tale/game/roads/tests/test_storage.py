
import smart_imports

smart_imports.all()


class RoadsStorageTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.p1, self.p2, self.p3 = game_logic.create_test_map()
        self.storage = storage.RoadsStorage()
        self.storage.sync()

    def test_initialization(self):
        test_storage = storage.RoadsStorage()
        self.assertEqual(test_storage._data, {})
        self.assertEqual(test_storage._version, None)

    def test_sync(self):
        self.assertEqual(len(self.storage._data), 2)

        road = models.Road.objects.order_by('?')[0]
        road.length = 666
        road.save()

        self.storage.sync()
        self.assertFalse(self.storage[road.id].length == 666)

        self.storage.sync(force=True)
        self.assertTrue(self.storage[road.id].length == 666)

    def test_sync_after_settings_update(self):
        self.assertEqual(len(self.storage._data), 2)

        road = models.Road.objects.order_by('?')[0]
        road.length = 666
        road.save()

        self.storage.sync()
        self.assertFalse(self.storage[road.id].length == 666)

        global_settings[self.storage.SETTINGS_KEY] = uuid.uuid4().hex

        self.storage.sync()
        self.assertTrue(self.storage[road.id].length == 666)

    def test_getitem_wrong_id(self):
        self.assertRaises(exceptions.RoadsStorageError, self.storage.__getitem__, 666)

    def test_getitem(self):
        road = models.Road.objects.order_by('?')[0]
        self.assertEqual(self.storage[road.id].id, road.id)

    def test_get(self):
        road = models.Road.objects.order_by('?')[0]
        self.assertEqual(self.storage.get(666, self.storage[road.id]), self.storage[road.id])
        self.assertEqual(self.storage.get(road.id, 666).id, road.id)

    def test_all(self):
        self.assertEqual(len(self.storage.all()), 2)

    def test_contains(self):
        road = models.Road.objects.order_by('?')[0]
        self.assertTrue(road.id in self.storage)
        self.assertFalse(666 in self.storage)
