# coding: utf-8
from django.test import TestCase

from game.game_info import RACE
from game.persons.models import PERSON_TYPE
from game.map.places.modifiers import MODIFIERS


class ModifiersTests(TestCase):

    def setUp(self):
        pass

    def test_all_professions_covered(self):
        for modifier in MODIFIERS.values():
            for person_type in PERSON_TYPE._ALL:
                self.assertTrue(person_type in modifier.PERSON_EFFECTS)

    def test_all_races_covered(self):
        for modifier in MODIFIERS.values():
            for race in RACE._ALL:
                self.assertTrue(race in modifier.RACE_EFFECTS)
