
import smart_imports

smart_imports.all()


class BaseMagicMapTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_magic_setupped(self):
        for x in range(map_conf.settings.WIDTH):
            for y in range(map_conf.settings.HEIGHT):
                self.assertTrue(storage.cells(x, y).magic > 0)

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
        self.place_1.effects.add(game_effects.Effect(name='test', attribute=places_relations.ATTRIBUTE.SAFETY, value=-1000))

        self.place_1.refresh_attributes()

        storage.cells.sync(force=True)

        self.assertAlmostEqual(storage.cells(self.place_1.x, self.place_1.y).safety, c.CELL_SAFETY_MIN)

    def test_refresh_attributes__safety__max_value(self):
        self.place_1.effects.add(game_effects.Effect(name='test', attribute=places_relations.ATTRIBUTE.SAFETY, value=1000))

        self.place_1.refresh_attributes()

        storage.cells.sync(force=True)

        self.assertAlmostEqual(storage.cells(self.place_1.x, self.place_1.y).safety, 1)

    def test_transport__min_value(self):
        self.place_1.effects.add(game_effects.Effect(name='test', attribute=places_relations.ATTRIBUTE.TRANSPORT, value=-1000))

        self.place_1.refresh_attributes()

        storage.cells.sync(force=True)

        self.assertAlmostEqual(storage.cells(self.place_1.x, self.place_1.y).transport, c.CELL_TRANSPORT_MIN)
