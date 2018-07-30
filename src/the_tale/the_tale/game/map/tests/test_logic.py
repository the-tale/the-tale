
import smart_imports

smart_imports.all()


class LogicTests(utils_testcase.TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()
        game_logic.create_test_map()

    def test_get_terrain_linguistics_restrictions(self):
        all_restrictions = set()
        for terrain in relations.TERRAIN.records:
            all_restrictions.add(logic.get_terrain_linguistics_restrictions(terrain))

        self.assertEqual(len(relations.TERRAIN.records), len(all_restrictions))
