# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.places.modifiers import CITY_MODIFIERS
from the_tale.game.relations import RACE

from the_tale.game.persons import economic


class RelationsTests(testcase.TestCase):

    def setUp(self):
        super(RelationsTests, self).setUp()

    def test_profession_to_race_mastery(self):
        for profession, masteries in economic.PROFESSION_TO_RACE.items():
            self.assertEqual(len(masteries), len(RACE.records))

            self.assertTrue(all([0 < mastery < 1.1201 for mastery in masteries.values()]))

        # check, if race id's not changed
        self.assertEqual(RACE.HUMAN.value, 0)
        self.assertEqual(RACE.ELF.value, 1)
        self.assertEqual(RACE.ORC.value, 2)
        self.assertEqual(RACE.GOBLIN.value, 3)
        self.assertEqual(RACE.DWARF.value, 4)

    def test_profession_to_city_specialization(self):
        for profession, specializations in economic.PROFESSION_TO_SPECIALIZATIONS.items():
            self.assertEqual(len(specializations), len(CITY_MODIFIERS.records))

            self.assertTrue(all([-10 <= effect <= 10 for effect in specializations.values()]))
