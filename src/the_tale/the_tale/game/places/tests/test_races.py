
import smart_imports

smart_imports.all()


E = 0.001


class RacesTests(utils_testcase.TestCase):

    def setUp(self):
        super(RacesTests, self).setUp()
        self.p1, self.p2, self.p3 = game_logic.create_test_map()

        for person in persons_storage.persons.all():
            politic_power_logic.add_power_impacts([game_tt_services.PowerImpact.hero_2_person(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                                                              hero_id=666,
                                                                                              person_id=person.id,
                                                                                              amount=1000),
                                                   game_tt_services.PowerImpact.hero_2_person(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                                                              hero_id=777,
                                                                                              person_id=person.id,
                                                                                              amount=2000)])
            person.attrs.demographics_pressure = 1

        politic_power_storage.persons.reset()

    def test_initialize(self):
        for race in game_relations.RACE.records:
            self.assertEqual(self.p1.races.get_race_percents(race), 1.0 / len(game_relations.RACE.records))

    def test_serialize(self):
        for i, race in enumerate(game_relations.RACE.records):
            self.p1.races._races[race] = i

        self.assertEqual(self.p1.races.serialize(), races.Races.deserialize(self.p1.races.serialize()).serialize())

    def test_get_next_races__no_trends(self):
        self.assertEqual(self.p1.races.get_next_races([]), self.p1.races._races)

    def test_get_next_races(self):
        self.assertTrue(1 - E < sum(self.p1.races._races.values()) < 1 + E)

        old_races = {race: 1.0 / len(game_relations.RACE.records) for race in game_relations.RACE.records}

        self.p1.races._races = copy.copy(old_races)

        checked_race = self.p1.persons[0].race

        next_races = self.p1.races.get_next_races(persons=[self.p1.persons[0]])

        for race in game_relations.RACE.records:
            if race == checked_race:
                self.assertTrue(next_races[race] > old_races[race])
            else:
                self.assertTrue(next_races[race] < old_races[race])

        self.assertTrue(1 - E < sum(self.p1.races._races.values()) < 1 + E)

    # @mock.patch('the_tale.game.jobs.job.Job.give_power', lambda obj, power: None)
    def test_get_next_races__cup(self):
        self.assertEqual(len(self.p1.persons), 3)

        fractions = {self.p1.persons[0].id: 0.75,
                     self.p1.persons[1].id: 0.25,
                     self.p1.persons[2].id: 0.00}

        self.p1.persons[0].race = game_relations.RACE.ORC
        self.p1.persons[1].race = game_relations.RACE.ELF
        self.p1.persons[2].race = game_relations.RACE.GOBLIN

        with mock.patch('the_tale.game.politic_power.storage.PowerStorage.total_power_fraction',
                        lambda self, person_id: fractions.get(person_id, 0)):
            for i in range(10000):
                self.p1.races.update(self.p1.persons)

        self.assertTrue(0.74 < self.p1.races.get_race_percents(game_relations.RACE.ORC) < 0.76)
        self.assertTrue(0.24 < self.p1.races.get_race_percents(game_relations.RACE.ELF) < 0.26)
        self.assertTrue(0.0 < self.p1.races.get_race_percents(game_relations.RACE.GOBLIN) < 0.01)

    def test_get_next_races__no_less_then_zero(self):
        self.assertTrue(1 - E < sum(self.p1.races._races.values()) < 1 + E)

        old_races = {race: 0.0 for race in game_relations.RACE.records}

        self.p1.races._races = copy.copy(old_races)

        next_races = self.p1.races.get_next_races(persons=self.p1.persons)

        for percents in list(next_races.values()):
            self.assertTrue(percents >= 0)

    def test_get_next_races__demographics_pressure(self):
        person_1 = self.p1.persons[0]
        person_2 = self.p2.persons[0]

        person_2.race = game_relations.RACE.random(exclude=(person_1.race,))

        old_races = races.Races()

        old_next_races = old_races.get_next_races((person_1, person_2))

        self.assertTrue(1 - E < sum(old_next_races.values()) < 1 + E)

        person_1.attrs.demographics_pressure = 2

        new_next_races = old_races.get_next_races((person_1, person_2))

        self.assertTrue(old_next_races[person_1.race] < new_next_races[person_1.race])
        self.assertTrue(old_next_races[person_2.race] > new_next_races[person_2.race])

        self.assertTrue(1 - E < sum(new_next_races.values()) < 1 + E)

    def test_update(self):
        next_races = self.p1.races.get_next_races(self.p1.persons)
        self.assertNotEqual(self.p1.races._races, next_races)
        self.p1.races.update(self.p1.persons)
        self.assertEqual(self.p1.races._races, next_races)

    def test_dominant_race(self):
        self.p1.races._races = {race: 0.5 for race in game_relations.RACE.records}
        self.p1.races._races[game_relations.RACE.ORC] = 1.0
        self.assertTrue(self.p1.races.dominant_race.is_ORC)
