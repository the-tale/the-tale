
import smart_imports

smart_imports.all()


class GetAvailablePositionsTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_get_available_positions(self):

        building = logic.create_building(self.place_1.persons[0], utg_name=game_names.generator().get_test_name(name='building-name'))

        positions = logic.get_available_positions(self.place_1.x, self.place_1.y)

        self.assertTrue(positions)

        for place in storage.places.all():
            self.assertFalse((place.x, place.y) in positions)

        for building in storage.buildings.all():
            self.assertFalse((building.x, building.y) in positions)

        for x, y in positions:
            self.assertTrue(0 <= x < map_conf.settings.WIDTH)
            self.assertTrue(0 <= y < map_conf.settings.HEIGHT)

    def test_dynamic_position_radius(self):
        with mock.patch('the_tale.game.balance.constants.BUILDING_POSITION_RADIUS', 2):
            positions = logic.get_available_positions(-3, -1)
            self.assertEqual(positions, set([(0, 0), (0, 1), (0, 2)]))

        with mock.patch('the_tale.game.balance.constants.BUILDING_POSITION_RADIUS', 2):
            positions = logic.get_available_positions(-4, -1)
            self.assertEqual(positions, set([(0, 0), (0, 1), (0, 2), (0, 3)]))


class TTPowerImpactsTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.actor_type = tt_api_impacts.OBJECT_TYPE.HERO
        self.actor_id = 666
        self.amount = 100500
        self.fame = 1000

        self.expected_power = round(self.place_1.attrs.freedom * self.amount)

    def test_inner_circle(self):
        impacts = list(logic.tt_power_impacts(inner_circle=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              place=self.place_1,
                                              amount=self.amount,
                                              fame=self.fame))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.JOB_PLACE_POSITIVE,
                                                            target_id=self.place_1.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.FAME,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=self.fame)])

    def test_outer_circle(self):
        impacts = list(logic.tt_power_impacts(inner_circle=False,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              place=self.place_1,
                                              amount=self.amount,
                                              fame=self.fame))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.FAME,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=self.fame)])

    def test_amount_below_zero(self):
        impacts = list(logic.tt_power_impacts(inner_circle=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              place=self.place_1,
                                              amount=-self.amount,
                                              fame=-self.fame))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=-self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.JOB_PLACE_NEGATIVE,
                                                            target_id=self.place_1.id,
                                                            amount=abs(self.expected_power))])

    def test_fame_only_for_hero(self):
        actor_type = tt_api_impacts.OBJECT_TYPE.random(exclude=(tt_api_impacts.OBJECT_TYPE.HERO,))

        impacts = list(logic.tt_power_impacts(inner_circle=True,
                                              actor_type=actor_type,
                                              actor_id=self.actor_id,
                                              place=self.place_1,
                                              amount=self.amount,
                                              fame=self.fame))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                                            actor_type=actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.JOB_PLACE_POSITIVE,
                                                            target_id=self.place_1.id,
                                                            amount=self.expected_power)])

    def test_zero(self):
        impacts = list(logic.tt_power_impacts(inner_circle=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              place=self.place_1,
                                              amount=0,
                                              fame=0))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=0),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.JOB_PLACE_POSITIVE,
                                                            target_id=self.place_1.id,
                                                            amount=0)])


def fake_tt_power_impacts(**kwargs):
    yield kwargs


class ImpactsFromHeroTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.hero = heroes_logic.load_hero(account_id=self.account.id)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, place: False)
    def test_can_not_change_power(self):
        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        place=self.place_1,
                                                        power=1000,
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': 0,
                                             'fame': c.HERO_FAME_PER_HELP,
                                             'inner_circle': False,
                                             'place': self.place_1}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, place: True)
    def test_can_change_power(self):
        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        place=self.place_1,
                                                        power=1000,
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': 1000,
                                             'fame': c.HERO_FAME_PER_HELP,
                                             'inner_circle': False,
                                             'place': self.place_1}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, place: True)
    def test_inner_circle(self):
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.PLACE, self.place_1)

        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        place=self.place_1,
                                                        power=1000,
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': 1000,
                                             'fame': c.HERO_FAME_PER_HELP,
                                             'inner_circle': True,
                                             'place': self.place_1}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, place: True)
    def test_power_below_zero(self):
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.PLACE, self.place_1)

        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        place=self.place_1,
                                                        power=-1000,
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': -1000,
                                             'fame': 0,
                                             'inner_circle': True,
                                             'place': self.place_1}])


class PlaceJobTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        game_tt_services.debug_clear_service()

        self.job = jobs_logic.create_job(logic.PlaceJob)

    def test_static_values(self):
        self.assertEqual(self.job.ACTOR, 'place')
        self.assertTrue(self.job.ACTOR_TYPE.is_PLACE)
        self.assertTrue(self.job.POSITIVE_TARGET_TYPE.is_JOB_PLACE_POSITIVE)
        self.assertTrue(self.job.NEGATIVE_TARGET_TYPE.is_JOB_PLACE_NEGATIVE)
        self.assertEqual(self.job.NORMAL_POWER, f.normal_job_power(politic_power_conf.settings.PLACE_INNER_CIRCLE_SIZE) * 2)

    def test_load_power(self):
        with mock.patch('the_tale.game.politic_power.logic.get_job_power', mock.Mock(return_value=666)) as get_job_power:
            self.assertEqual(self.job.load_power(self.place_1.id), 666)

        get_job_power.assert_called_once_with(place_id=self.place_1.id)

    def test_load_inner_circle(self):
        with mock.patch('the_tale.game.politic_power.logic.get_inner_circle', mock.Mock(return_value=666)) as get_inner_circle:
            self.assertEqual(self.job.load_inner_circle(self.place_1.id), 666)

        get_inner_circle.assert_called_once_with(place_id=self.place_1.id)

    def test_get_job_power(self):
        with mock.patch('the_tale.game.politic_power.storage.PowerStorage.total_power_fraction',
                        lambda self, target_id: 0.5):
            self.assertEqual(self.job.get_job_power(self.place_1.id), 0.875)

    def test_get_project_name(self):
        name = self.place_1.utg_name.form(utg_words.Properties(utg_relations.CASE.GENITIVE))
        self.assertEqual(self.job.get_project_name(self.place_1.id), 'Проект города {name}'.format(name=name))

    def test_get_objects(self):
        self.assertEqual(self.job.get_objects(self.place_1.id),
                         {'person': None,
                          'place': self.place_1})

    def test_get_effects_priorities(self):
        self.assertEqual(self.job.get_effects_priorities(self.place_1.id),
                         {effect: 1 for effect in jobs_effects.EFFECT.records})


class GetStartPlaceForRaceTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.places = list(game_logic.create_test_map())
        self.races = {place.race for place in self.places}

        self.assertTrue(len(self.places), 3)

    def test_no_frontier(self):
        unexisted_race = game_relations.RACE.random(exclude=self.races)

        for target_place in self.places:
            for place in self.places:
                place.is_frontier = (place.id != target_place.id)

            found_place = logic.get_start_place_for_race(unexisted_race)

            self.assertEqual(found_place.id, target_place.id)

    def test_best_security(self):
        unexisted_race = game_relations.RACE.random(exclude=self.races)

        for place in self.places:
            place.is_frontier = False
            place.attrs.safety = random.uniform(0, 1)

        found_place = logic.get_start_place_for_race(unexisted_race)

        self.assertTrue(all(place.attrs.safety <= found_place.attrs.safety
                            for place in self.places))

    @mock.patch('the_tale.game.places.conf.settings.START_PLACE_SAFETY_PERCENTAGE', 1.0)
    def test_filter_by_race(self):
        race = game_relations.RACE.random()

        for place in self.places:
            place.is_frontier = False

        self.places[0].race = race
        self.places[0].attrs.safety = 0.1

        self.places[1].race = game_relations.RACE.random(exclude=[race])
        self.places[1].attrs.safety = 1.0

        self.places[2].race = race
        self.places[2].attrs.safety = 0.2

        found_place = logic.get_start_place_for_race(race)

        self.assertEqual(found_place.id, self.places[2].id)

    @mock.patch('the_tale.game.places.conf.settings.START_PLACE_SAFETY_PERCENTAGE', 0.2)
    def test_filter_by_race__after_safety_limitation(self):
        race = game_relations.RACE.random()

        for place in self.places:
            place.is_frontier = False

        self.places[0].race = race
        self.places[0].attrs.safety = 0.1

        self.places[1].race = game_relations.RACE.random(exclude=[race])
        self.places[1].attrs.safety = 1.0

        self.places[2].race = race
        self.places[2].attrs.safety = 0.2

        found_place = logic.get_start_place_for_race(race)

        self.assertEqual(found_place.id, self.places[1].id)


class ChoosePlaceCellByTerrainTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.places = list(game_logic.create_test_map())

        self.assertTrue(len(map_storage.cells.place_cells(self.places[0].id)) > 1)

    def test_no_terrains(self):
        expected_cells = set(map_storage.cells.place_cells(self.places[0].id))

        cells = set()

        while cells != expected_cells:
            cells.add(logic.choose_place_cell_by_terrain(self.places[0].id, terrains=()))

    def test_filter_by_terrains__has_terrains(self):
        x, y = logic.choose_place_cell_by_terrain(self.places[0].id, terrains=())

        terrain = map_storage.cells(x, y).terrain

        for i in range(100):
            test_x, test_y = logic.choose_place_cell_by_terrain(self.places[0].id, terrains=())
            self.assertEqual(map_storage.cells(test_x, test_y).terrain, terrain)

    def test_filter_by_terrains__no_terrains(self):
        expected_cells = set(map_storage.cells.place_cells(self.places[0].id))

        cells = set()

        existed_terrains = {map_storage.cells(*cell).terrain for cell in expected_cells}

        unexisted_terrain = map_relations.TERRAIN.random(exclude=existed_terrains)

        while cells != expected_cells:
            cells.add(logic.choose_place_cell_by_terrain(self.places[0].id, terrains=(unexisted_terrain,)))


class SyncPowerEconomicTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.places = game_logic.create_test_map()

        game_tt_services.debug_clear_service()

    def test(self):
        impacts = []
        for power, place in zip((100, 300, 200), self.places):
            impacts.append(game_tt_services.PowerImpact.hero_2_place(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                                     hero_id=1,
                                                                     place_id=place.id,
                                                                     amount=power))
        politic_power_logic.add_power_impacts(impacts)

        politic_power_storage.places.sync(force=True)

        logic.sync_power_economic(self.places, 5)

        self.assertEqual(self.places[0].attrs.power_economic, 2)
        self.assertEqual(self.places[1].attrs.power_economic, 4)
        self.assertEqual(self.places[2].attrs.power_economic, 3)


class SyncMoneyEconomicTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.places = game_logic.create_test_map()

        game_tt_services.debug_clear_service()

    def test(self):
        for money, place in zip((100, 300, 200), self.places):
            logic.register_money_transaction(hero_id=1, place_id=place.id, amount=money)

        logic.sync_money_economic(self.places, 5)

        self.assertEqual(self.places[0].attrs.money_economic, 2)
        self.assertEqual(self.places[1].attrs.money_economic, 4)
        self.assertEqual(self.places[2].attrs.money_economic, 3)
