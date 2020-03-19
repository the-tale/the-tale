
import smart_imports

smart_imports.all()


class BaseMagicMapTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_roads_on_cell(self):
        self.assertEqual(len(storage.cells(0, 0).roads_ids), 0)
        self.assertEqual(len(storage.cells(self.place_1.x, self.place_1.y).roads_ids), 1)
        self.assertEqual(len(storage.cells(self.place_2.x, self.place_2.y).roads_ids), 2)
        self.assertEqual(len(storage.cells(self.place_3.x, self.place_3.y).roads_ids), 1)


class EffectsTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_refresh_attributes__safety__min_value(self):
        places_logic.register_effect(place_id=self.place_1.id,
                                     attribute=places_relations.ATTRIBUTE.SAFETY,
                                     value=-1000,
                                     name='test',
                                     refresh_effects=True,
                                     refresh_places=True)

        self.place_1.refresh_attributes()

        storage.cells.sync(force=True)

        self.assertAlmostEqual(storage.cells(self.place_1.x, self.place_1.y).safety, c.CELL_SAFETY_MIN)

    def test_refresh_attributes__safety__max_value(self):

        places_logic.register_effect(place_id=self.place_1.id,
                                     attribute=places_relations.ATTRIBUTE.SAFETY,
                                     value=1000,
                                     name='test',
                                     refresh_effects=True,
                                     refresh_places=True)

        self.place_1.refresh_attributes()

        storage.cells.sync(force=True)

        self.assertAlmostEqual(storage.cells(self.place_1.x, self.place_1.y).safety, c.CELL_SAFETY_MAX)

    def test_transport__min_value(self):
        places_logic.register_effect(place_id=self.place_1.id,
                                     attribute=places_relations.ATTRIBUTE.TRANSPORT,
                                     value=-1000,
                                     name='test',
                                     refresh_effects=True,
                                     refresh_places=True)

        storage.cells.sync(force=True)

        self.assertAlmostEqual(storage.cells(self.place_1.x, self.place_1.y).transport, c.CELL_TRANSPORT_MIN)
