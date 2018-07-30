

import smart_imports

smart_imports.all()


class TestPowerStorage(storage.PowerStorage):

    TARGET_TYPE = tt_api_impacts.OBJECT_TYPE.PERSON

    def __init__(self, targets_ids, **kwargs):
        super().__init__(**kwargs)
        self._test_targets_ids = targets_ids

    def _tt_targets_ids(self):
        return self._test_targets_ids

    def _update_fractions(self):
        self._inner_power_fraction = {target_id: target_id / 100.0 for target_id in self._test_targets_ids}
        self._outer_power_fraction = {target_id: target_id / 10.0 for target_id in self._test_targets_ids}


class PowerStorageTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        game_tt_services.debug_clear_service()

        self.storage = TestPowerStorage(targets_ids=[10, 20, 30, 40, 50])

        logic.add_power_impacts([game_tt_services.PowerImpact.hero_2_person(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                                            hero_id=1,
                                                                            person_id=10,
                                                                            amount=100),
                                 game_tt_services.PowerImpact.hero_2_person(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                                            hero_id=2,
                                                                            person_id=20,
                                                                            amount=200),
                                 game_tt_services.PowerImpact.hero_2_person(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                                            hero_id=1,
                                                                            person_id=30,
                                                                            amount=-300),
                                 game_tt_services.PowerImpact.hero_2_person(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                                            hero_id=3,
                                                                            person_id=40,
                                                                            amount=-400),
                                 game_tt_services.PowerImpact.hero_2_person(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                                            hero_id=4,
                                                                            person_id=50,
                                                                            amount=500)])

    def test_initialize(self):
        self.assertEqual(self.storage.turn, None)
        self.assertEqual(self.storage._inner_power, None)
        self.assertEqual(self.storage._outer_power, None)
        self.assertEqual(self.storage._inner_power_fraction, None)
        self.assertEqual(self.storage._outer_power_fraction, None)

    def test_sync(self):
        self.storage.sync()

        self.assertEqual(self.storage.turn, 0)
        self.assertEqual(self.storage._inner_power, {10: 100,
                                                     20: 200,
                                                     30: 0,
                                                     40: -400,
                                                     50: 0})
        self.assertEqual(self.storage._outer_power, {10: 0,
                                                     20: 0,
                                                     30: -300,
                                                     40: 0,
                                                     50: 500})
        self.assertEqual(self.storage._inner_power_fraction, {10: 0.1, 20: 0.2, 30: 0.3, 40: 0.4, 50: 0.5})
        self.assertEqual(self.storage._outer_power_fraction, {10: 1, 20: 2, 30: 3, 40: 4, 50: 5})

    def test_sync__no_power(self):
        game_tt_services.debug_clear_service()
        self.storage.sync()

        self.assertEqual(self.storage.turn, 0)
        self.assertEqual(self.storage._inner_power, {10: 0, 20: 0, 30: 0, 40: 0, 50: 0})
        self.assertEqual(self.storage._outer_power, {10: 0, 20: 0, 30: 0, 40: 0, 50: 0})

    def test_sync__turn_cache(self):
        self.storage.sync()

        logic.add_power_impacts([game_tt_services.PowerImpact.hero_2_person(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                                            hero_id=1,
                                                                            person_id=10,
                                                                            amount=666)])
        self.storage.sync()

        self.assertEqual(self.storage.turn, 0)
        self.assertEqual(self.storage._inner_power, {10: 100,
                                                     20: 200,
                                                     30: 0,
                                                     40: -400,
                                                     50: 0})
        self.assertEqual(self.storage._outer_power, {10: 0,
                                                     20: 0,
                                                     30: -300,
                                                     40: 0,
                                                     50: 500})

    def test_sync__turn_cache_reset(self):
        self.storage.sync()

        logic.add_power_impacts([game_tt_services.PowerImpact.hero_2_person(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                                            hero_id=1,
                                                                            person_id=10,
                                                                            amount=666)])
        game_turn.increment()

        self.storage.sync()

        self.assertEqual(self.storage.turn, 1)
        self.assertEqual(self.storage._inner_power, {10: 100 + 666,
                                                     20: 200,
                                                     30: 0,
                                                     40: -400,
                                                     50: 0})
        self.assertEqual(self.storage._outer_power, {10: 0,
                                                     20: 0,
                                                     30: -300,
                                                     40: 0,
                                                     50: 500})

    def test_total_power_fraction(self):
        self.assertEqual(self.storage.total_power_fraction(10), (0.1 + 1) / 2)

    def test_inner_power_fraction(self):
        self.assertEqual(self.storage.inner_power_fraction(10), 0.1)

    def test_inner_power(self):
        self.assertEqual(self.storage.inner_power(10), 100)

    def test_outer_power_fraction(self):
        self.assertEqual(self.storage.outer_power_fraction(10), 1)

    def test_outer_power(self):
        self.assertEqual(self.storage.outer_power(10), 0)

    def test_ui_info(self):
        self.assertEqual(self.storage.ui_info(30),
                         {'inner': {'value': 0,
                                    'fraction': 0.3},
                          'outer': {'value': -300,
                                    'fraction': 3},
                          'fraction': (3 + 0.3) / 2})


class PlacesPowerStorageTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.places = game_logic.create_test_map()

        game_tt_services.debug_clear_service()

    def test_targets_ids(self):
        self.assertCountEqual(storage.places._tt_targets_ids(),
                              [place.id for place in self.places])

    def check_fractions(self):
        storage.places._inner_power = {self.places[0].id: 75,
                                       self.places[1].id: 50,
                                       self.places[2].id: 25}

        storage.places._outer_power = {self.places[0].id: 5,
                                       self.places[1].id: 0,
                                       self.places[2].id: 5}

        storage.places._update_fractions()

        self.assertEqual(storage.places._inner_power_fraction, {self.places[0].id: 0.75,
                                                                self.places[1].id: 1.0,
                                                                self.places[2].id: 0.25})
        self.assertEqual(storage.places._outer_power_fraction, {self.places[0].id: 0.5,
                                                                self.places[1].id: 0,
                                                                self.places[2].id: 0.5})

    def test_update_fractions__core(self):
        self.places[1].is_frontier = True
        self.check_fractions()

    def test_update_fractions__frontier(self):
        self.places[0].is_frontier = True
        self.places[2].is_frontier = True
        self.check_fractions()


class PersonsPowerStorageTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.places = game_logic.create_test_map()

        self.persons = [place.persons for place in self.places]

        game_tt_services.debug_clear_service()

    def test_targets_ids(self):
        self.assertEqual(storage.persons._tt_targets_ids(),
                         [person.id for person in persons_storage.persons.all()])

    def test_update_fractions(self):
        for place in self.places:
            self.assertEqual(len(place.persons), 3)

        storage.persons._inner_power = {self.persons[0][0].id: 75,
                                        self.persons[0][1].id: 25,
                                        self.persons[0][2].id: 0,
                                        self.persons[1][0].id: 10,
                                        self.persons[1][1].id: 80,
                                        self.persons[1][2].id: 10,
                                        self.persons[2][0].id: 54,
                                        self.persons[2][1].id: 30,
                                        self.persons[2][2].id: 16}

        storage.persons._outer_power = {self.persons[0][0].id: 30,
                                        self.persons[0][1].id: 30,
                                        self.persons[0][2].id: 40,
                                        self.persons[1][0].id: 1,
                                        self.persons[1][1].id: 4,
                                        self.persons[1][2].id: 5,
                                        self.persons[2][0].id: 100,
                                        self.persons[2][1].id: 200,
                                        self.persons[2][2].id: 200}

        storage.persons._update_fractions()

        storage.persons._inner_power_fraction = {self.persons[0][0].id: 0.75,
                                                 self.persons[0][1].id: 0.25,
                                                 self.persons[0][2].id: 0,
                                                 self.persons[1][0].id: 0.10,
                                                 self.persons[1][1].id: 0.80,
                                                 self.persons[1][2].id: 0.10,
                                                 self.persons[2][0].id: 0.54,
                                                 self.persons[2][1].id: 0.30,
                                                 self.persons[2][2].id: 0.16}

        storage.persons._outer_power_fraction = {self.persons[0][0].id: 0.30,
                                                 self.persons[0][1].id: 0.30,
                                                 self.persons[0][2].id: 0.40,
                                                 self.persons[1][0].id: 0.1,
                                                 self.persons[1][1].id: 0.4,
                                                 self.persons[1][2].id: 0.5,
                                                 self.persons[2][0].id: 0.2,
                                                 self.persons[2][1].id: 0.4,
                                                 self.persons[2][2].id: 0.4}
