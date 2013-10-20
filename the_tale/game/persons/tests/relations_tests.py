# coding: utf-8

from common.utils import testcase

from game.balance.enums import CITY_MODIFIERS
from game.relations import RACE

from game.persons.relations import PROFESSION_TO_RACE_MASTERY, PROFESSION_TO_CITY_MODIFIERS

class RelationsTests(testcase.TestCase):

    def setUp(self):
        super(RelationsTests, self).setUp()

    def test_profession_to_race_mastery(self):
        for profession, masteries in PROFESSION_TO_RACE_MASTERY.items():
            self.assertEqual(len(masteries), len(RACE._records))

            self.assertTrue(all([0 < mastery < 1.0001 for mastery in masteries.values()]))

        # check, if race id's not changed
        self.assertEqual(RACE.HUMAN.value, 0)
        self.assertEqual(RACE.ELF.value, 1)
        self.assertEqual(RACE.ORC.value, 2)
        self.assertEqual(RACE.GOBLIN.value, 3)
        self.assertEqual(RACE.DWARF.value, 4)

    def test_profession_to_city_specialization(self):
        for profession, specializations in PROFESSION_TO_CITY_MODIFIERS.items():
            self.assertEqual(len(specializations), len(CITY_MODIFIERS._ALL))

            self.assertTrue(all([-10 <= effect <= 10 for effect in specializations.values()]))
