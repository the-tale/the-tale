
import smart_imports

smart_imports.all()


class RelationsTests(utils_testcase.TestCase):

    def setUp(self):
        super(RelationsTests, self).setUp()

    def test_profession_to_race_mastery(self):
        for profession, masteries in list(economic.PROFESSION_TO_RACE.items()):
            self.assertEqual(len(masteries), len(game_relations.RACE.records))

            self.assertTrue(all([0 < mastery < 1.1201 for mastery in list(masteries.values())]))

        # check, if race id's not changed
        self.assertEqual(game_relations.RACE.HUMAN.value, 0)
        self.assertEqual(game_relations.RACE.ELF.value, 1)
        self.assertEqual(game_relations.RACE.ORC.value, 2)
        self.assertEqual(game_relations.RACE.GOBLIN.value, 3)
        self.assertEqual(game_relations.RACE.DWARF.value, 4)
