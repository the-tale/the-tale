# coding: utf-8
import copy

import mock

from the_tale.common.utils import testcase

from the_tale.game.relations import RACE

from the_tale.game.logic import create_test_map
from the_tale.game.persons import storage as persons_storage

from .. import races


E = 0.001

class RacesTests(testcase.TestCase):

    @mock.patch('the_tale.game.jobs.job.Job.give_power', lambda obj, power: None)
    def setUp(self):
        super(RacesTests, self).setUp()
        self.p1, self.p2, self.p3 = create_test_map()

        for person in persons_storage.persons.all():
            person.politic_power.change_power(person, hero_id=666, has_in_preferences=False, power=1000)
            person.politic_power.change_power(person, hero_id=777, has_in_preferences=True, power=2000)
            person.attrs.demographics_pressure = 1

    def test_initialize(self):
        for race in RACE.records:
            self.assertEqual(self.p1.races.get_race_percents(race), 1.0 / len(RACE.records))

    def test_serialize(self):
        for i, race in enumerate(RACE.records):
            self.p1.races._races[race] = i

        self.assertEqual(self.p1.races.serialize(), races.Races.deserialize(self.p1.races.serialize()).serialize())


    def test_get_next_races__no_trends(self):
        self.assertEqual(self.p1.races.get_next_races([]), self.p1.races._races)

    def test_get_next_races(self):
        self.assertTrue(1 - E < sum(self.p1.races._races.values()) < 1 + E )

        old_races = {race: 1.0 / len(RACE.records) for race in RACE.records}

        self.p1.races._races = copy.copy(old_races)

        checked_race = self.p1.persons[0].race

        next_races = self.p1.races.get_next_races(persons=[self.p1.persons[0]])

        for race in RACE.records:
            if race == checked_race:
                self.assertTrue(next_races[race] > old_races[race])
            else:
                self.assertTrue(next_races[race] < old_races[race])

        self.assertTrue(1 - E < sum(self.p1.races._races.values()) < 1 + E )

    @mock.patch('the_tale.game.jobs.job.Job.give_power', lambda obj, power: None)
    def test_get_next_races__cup(self):
        self.assertEqual(len(self.p1.persons), 3)

        self.p1.persons[0].race = RACE.ORC
        self.p1.persons[0].politic_power.outer_power = 1000
        self.p1.persons[0].politic_power.inner_power = 3000
        self.p1.persons[1].race = RACE.ELF
        self.p1.persons[1].politic_power.outer_power = 500
        self.p1.persons[1].politic_power.inner_power = 1500
        self.p1.persons[2].race = RACE.GOBLIN
        self.p1.persons[2].politic_power.outer_power = 0
        self.p1.persons[2].politic_power.inner_power = 0

        for i in xrange(10000):
            self.p1.races.update(self.p1.persons)

        self.assertTrue(0.66 < self.p1.races.get_race_percents(RACE.ORC) < 0.67)
        self.assertTrue(0.33 < self.p1.races.get_race_percents(RACE.ELF) < 0.34)
        self.assertTrue(0.0 < self.p1.races.get_race_percents(RACE.GOBLIN) < 0.01)

    def test_get_next_races__no_less_then_zero(self):
        self.assertTrue(1 - E < sum(self.p1.races._races.values()) < 1 + E )

        old_races = {race: 0.0 for race in RACE.records}

        self.p1.races._races = copy.copy(old_races)

        next_races = self.p1.races.get_next_races(persons=self.p1.persons)

        for percents in next_races.values():
            self.assertTrue(percents >= 0)


    def test_get_next_races__demographics_pressure(self):
        person_1 = self.p1.persons[0]
        person_2 = self.p2.persons[0]

        person_2.race = RACE.random(exclude=(person_1.race,))

        old_races = races.Races()

        old_next_races = old_races.get_next_races((person_1, person_2))

        self.assertTrue(1 - E < sum(old_next_races.values()) < 1 + E )

        person_1.attrs.demographics_pressure = 2

        new_next_races = old_races.get_next_races((person_1, person_2))

        self.assertTrue(old_next_races[person_1.race] < new_next_races[person_1.race])
        self.assertTrue(old_next_races[person_2.race] > new_next_races[person_2.race])

        self.assertTrue(1 - E < sum(new_next_races.values()) < 1 + E )


    def test_update(self):
        next_races = self.p1.races.get_next_races(self.p1.persons)
        self.assertNotEqual(self.p1.races._races, next_races)
        self.p1.races.update(self.p1.persons)
        self.assertEqual(self.p1.races._races, next_races)

    def test_dominant_race(self):
        self.p1.races._races = {race: 0.5 for race in RACE.records}
        self.p1.races._races[RACE.ORC] = 1.0
        self.assertTrue(self.p1.races.dominant_race.is_ORC)
