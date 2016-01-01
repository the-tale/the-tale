# coding: utf-8
import copy

from the_tale.common.utils import testcase

from the_tale.game.relations import RACE

from the_tale.game.logic import create_test_map
from the_tale.game.persons import storage as persons_storage

from .. import races


E = 0.001

class RacesTests(testcase.TestCase):

    def setUp(self):
        super(RacesTests, self).setUp()
        self.p1, self.p2, self.p3 = create_test_map()

        for person in persons_storage.persons.all():
            person.power = 1000

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


    def test_get_next_races__cup(self):
        self.assertEqual(len(self.p1.persons), 3)

        self.p1.persons[0].race = RACE.ORC
        self.p1.persons[0].power = 1000
        self.p1.persons[1].race = RACE.ELF
        self.p1.persons[1].power = 500
        self.p1.persons[2].race = RACE.GOBLIN
        self.p1.persons[2].power = 0

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


    def test_update(self):
        next_races = self.p1.races.get_next_races(self.p1.persons)
        self.assertNotEqual(self.p1.races._races, next_races)
        self.p1.races.update(self.p1.persons)
        self.assertEqual(self.p1.races._races, next_races)

    def test_dominant_race(self):
        self.p1.races._races = {race: 0.5 for race in RACE.records}
        self.p1.races._races[RACE.ORC] = 1.0
        self.assertTrue(self.p1.races.dominant_race.is_ORC)
