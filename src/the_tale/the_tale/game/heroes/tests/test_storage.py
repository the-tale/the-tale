
import smart_imports

smart_imports.all()


class PositionDescriptionsStorageTests(utils_testcase.TestCase):

    def setUp(self):
        super(PositionDescriptionsStorageTests, self).setUp()
        self.place_1, self.place_2, _ = game_logic.create_test_map()

        storage.position_descriptions.clear()

    def test_clear(self):
        self.assertEqual(storage.position_descriptions._position_in_place_cache, {})
        self.assertEqual(storage.position_descriptions._position_near_place_cache, {})
        self.assertEqual(storage.position_descriptions._position_on_road_cache, {})
        self.assertEqual(storage.position_descriptions._actual_places_version, places_storage.places._version)

    def test_sync(self):
        with mock.patch('the_tale.game.heroes.storage.PositionDescriptionsStorage.clear') as clear:
            storage.position_descriptions.sync()

        self.assertEqual(clear.call_count, 0)

        places_storage.places.update_version()

        with mock.patch('the_tale.game.heroes.storage.PositionDescriptionsStorage.clear') as clear:
            storage.position_descriptions.sync()

        self.assertEqual(clear.call_count, 1)

    def test_text_in_place(self):
        text = storage.position_descriptions.text_in_place(self.place_1.id)
        self.assertTrue(text)
        self.assertEqual(storage.position_descriptions._position_in_place_cache, {self.place_1.id: text})

    def test_text_near_place(self):
        text = storage.position_descriptions.text_near_place(self.place_1.id)
        self.assertTrue(text)
        self.assertEqual(storage.position_descriptions._position_near_place_cache, {self.place_1.id: text})

    def test_text_on_road(self):
        text = storage.position_descriptions.text_on_road(self.place_1.id, self.place_2.id)
        self.assertTrue(text)
        self.assertEqual(storage.position_descriptions._position_on_road_cache, {(self.place_1.id, self.place_2.id): text})

    def text_in_wild_lands(self, place_id):
        self.assertEqual(storage.position_descriptions.text_in_wild_lands(), 'дикие земли')
