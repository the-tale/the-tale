
import smart_imports

smart_imports.all()


class GetTerrainLinguisticsRestrictionsTests(utils_testcase.TestCase):

    def setUp(self):
        super(GetTerrainLinguisticsRestrictionsTests, self).setUp()
        game_logic.create_test_map()

    def test_get_terrain_linguistics_restrictions(self):
        all_restrictions = set()
        for terrain in relations.TERRAIN.records:
            all_restrictions.add(logic.get_terrain_linguistics_restrictions(terrain))

        self.assertEqual(len(relations.TERRAIN.records), len(all_restrictions))


class GetPersonRacePercentsTests(utils_testcase.TestCase):

    def setUp(self):
        super(GetPersonRacePercentsTests, self).setUp()
        game_logic.create_test_map()

        game_tt_services.debug_clear_service()

    def test_normalized_sum(self):
        person_race_percents = map_logic.get_person_race_percents(persons_storage.persons.all())

        self.assertEqual(round(sum(person_race_percents.values())), 1.0)
