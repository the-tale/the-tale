# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.game.balance import formulas as f
from the_tale.game.balance import constants as c

from the_tale.game.places.modifiers import CITY_MODIFIERS


from the_tale.game.persons import economic
from the_tale.game.persons import relations


class RelationsTests(testcase.TestCase):

    def setUp(self):
        super(RelationsTests, self).setUp()

    def test_profession_to_city_specialization(self):
        for specializations in economic.PROFESSION_TO_SPECIALIZATIONS.values():
            self.assertEqual(len(specializations), len(CITY_MODIFIERS.records))

            self.assertTrue(all([-3 <= effect <= 3 for effect in list(specializations.values())]))


    def test_no_equal_specializations_bonuses(self):
        bonuses = set()

        for specializations in economic.PROFESSION_TO_SPECIALIZATIONS.values():
            specialization_bonuses = tuple([x[1] for x in sorted(specializations.items())])
            self.assertNotIn(specialization_bonuses, bonuses)
            bonuses.add(specialization_bonuses)


    def test_two_different_masters_can_any_specialization_on_10_city_size(self):

        place_size = 10
        person_power = 0.3

        for specialization in CITY_MODIFIERS.records:

            if specialization.is_NONE:
                continue

            best = 0

            for profession_1 in relations.PERSON_TYPE.records:
                for profession_2 in relations.PERSON_TYPE.records:
                    if profession_1 == profession_2:
                        continue

                    points_1 = f.place_specialization_from_person(person_points=economic.PROFESSION_TO_SPECIALIZATIONS[profession_1][specialization],
                                                                  politic_power_fraction=person_power,
                                                                  place_size_multiplier=f.place_specialization_modifier(place_size))

                    points_2 = f.place_specialization_from_person(person_points=economic.PROFESSION_TO_SPECIALIZATIONS[profession_2][specialization],
                                                                  politic_power_fraction=person_power,
                                                                  place_size_multiplier=f.place_specialization_modifier(place_size))

                    if best < points_1 + points_2:
                        best = points_1 + points_2

            self.assertTrue(c.PLACE_TYPE_NECESSARY_BORDER < best)


    def test_three_different_masters_can_any_specialization_on_7_city_size(self):

        place_size = 7
        person_power = 0.3

        for specialization in CITY_MODIFIERS.records:

            if specialization.is_NONE:
                continue

            best = 0

            for profession_1 in relations.PERSON_TYPE.records:
                for profession_2 in relations.PERSON_TYPE.records:
                    for profession_3 in relations.PERSON_TYPE.records:
                        if (profession_1 == profession_2 or
                            profession_1 == profession_3 or
                            profession_2 == profession_3):
                            continue

                        points_1 = f.place_specialization_from_person(person_points=economic.PROFESSION_TO_SPECIALIZATIONS[profession_1][specialization],
                                                                      politic_power_fraction=person_power,
                                                                      place_size_multiplier=f.place_specialization_modifier(place_size))

                        points_2 = f.place_specialization_from_person(person_points=economic.PROFESSION_TO_SPECIALIZATIONS[profession_2][specialization],
                                                                      politic_power_fraction=person_power,
                                                                      place_size_multiplier=f.place_specialization_modifier(place_size))

                        points_3 = f.place_specialization_from_person(person_points=economic.PROFESSION_TO_SPECIALIZATIONS[profession_3][specialization],
                                                                      politic_power_fraction=person_power,
                                                                      place_size_multiplier=f.place_specialization_modifier(place_size))

                        if best < points_1 + points_2 + points_3:
                            best = points_1 + points_2 + points_3

            self.assertTrue(c.PLACE_TYPE_NECESSARY_BORDER < best)
