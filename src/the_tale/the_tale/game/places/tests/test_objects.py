
import smart_imports

smart_imports.all()


TEST_FREEDOM = 3


class PlaceTests(helpers.PlacesTestsMixin,
                 utils_testcase.TestCase):

    def setUp(self):
        super(PlaceTests, self).setUp()
        tt_services.effects.cmd_debug_clear_service()

        self.p1, self.p2, self.p3 = game_logic.create_test_map()

    @mock.patch('the_tale.game.balance.constants.PLACE_NEW_PLACE_LIVETIME', 0)
    def test_is_new__false(self):
        self.assertFalse(self.p1.is_new)

    @mock.patch('the_tale.game.balance.constants.PLACE_NEW_PLACE_LIVETIME', 60)
    def test_is_new__true(self):
        self.assertTrue(self.p1.is_new)

    def test_sync_size__good_changing(self):
        self.p1.attrs.production = 10

        self.assertEqual(self.p1.attrs.goods, 0)
        self.p1.attrs.sync_size(2)
        self.assertEqual(self.p1.attrs.goods, 20)

        self.p1.attrs.production = -10
        self.p1.attrs.goods = 11
        self.p1.attrs.sync_size(1)
        self.assertEqual(self.p1.attrs.goods, 1)

    def test_sync_size__size_increased(self):
        self.p1.attrs.production = 10

        self.p1.attrs.goods = c.PLACE_GOODS_TO_LEVEL
        self.p1.attrs.size = 1
        self.p1.attrs.sync_size(1)
        self.assertEqual(self.p1.attrs.goods, c.PLACE_GOODS_TO_LEVEL * c.PLACE_GOODS_AFTER_LEVEL_UP)
        self.assertEqual(self.p1.attrs.size, 2)

        self.p1.attrs.goods = c.PLACE_GOODS_TO_LEVEL
        self.p1.attrs.size = 10
        self.p1.attrs.sync_size(1)
        self.assertEqual(self.p1.attrs.goods, c.PLACE_GOODS_TO_LEVEL)
        self.assertEqual(self.p1.attrs.size, 10)

    def test_sync_size__size_decreased(self):
        self.p1.attrs.production = -10

        self.p1.attrs.goods = 0
        self.p1.attrs.size = 2
        self.p1.attrs.sync_size(1)
        self.assertEqual(self.p1.attrs.goods, c.PLACE_GOODS_TO_LEVEL * c.PLACE_GOODS_AFTER_LEVEL_DOWN)
        self.assertEqual(self.p1.attrs.size, 1)

        self.p1.attrs.goods = 0
        self.p1.attrs.size = 1
        self.p1.attrs.sync_size(1)
        self.assertEqual(self.p1.attrs.goods, 0)
        self.assertEqual(self.p1.attrs.size, 1)

    def _create_test_exchanges(self):
        prototypes.ResourceExchangePrototype.create(place_1=self.p1,
                                                    place_2=self.p2,
                                                    resource_1=relations.RESOURCE_EXCHANGE_TYPE.PRODUCTION_SMALL,
                                                    resource_2=relations.RESOURCE_EXCHANGE_TYPE.NONE,
                                                    bill=None)

        prototypes.ResourceExchangePrototype.create(place_1=self.p1,
                                                    place_2=self.p3,
                                                    resource_1=relations.RESOURCE_EXCHANGE_TYPE.NONE,
                                                    resource_2=relations.RESOURCE_EXCHANGE_TYPE.PRODUCTION_LARGE,
                                                    bill=None)

        prototypes.ResourceExchangePrototype.create(place_1=self.p1,
                                                    place_2=self.p2,
                                                    resource_1=relations.RESOURCE_EXCHANGE_TYPE.SAFETY_SMALL,
                                                    resource_2=relations.RESOURCE_EXCHANGE_TYPE.NONE,
                                                    bill=None)

        prototypes.ResourceExchangePrototype.create(place_1=self.p1,
                                                    place_2=self.p3,
                                                    resource_1=relations.RESOURCE_EXCHANGE_TYPE.NONE,
                                                    resource_2=relations.RESOURCE_EXCHANGE_TYPE.SAFETY_LARGE,
                                                    bill=None)

        prototypes.ResourceExchangePrototype.create(place_1=self.p1,
                                                    place_2=self.p2,
                                                    resource_1=relations.RESOURCE_EXCHANGE_TYPE.TRANSPORT_SMALL,
                                                    resource_2=relations.RESOURCE_EXCHANGE_TYPE.NONE,
                                                    bill=None)

        prototypes.ResourceExchangePrototype.create(place_1=self.p1,
                                                    place_2=self.p3,
                                                    resource_1=relations.RESOURCE_EXCHANGE_TYPE.NONE,
                                                    resource_2=relations.RESOURCE_EXCHANGE_TYPE.TRANSPORT_LARGE,
                                                    bill=None)

        prototypes.ResourceExchangePrototype.create(place_1=self.p1,
                                                    place_2=None,
                                                    resource_1=relations.RESOURCE_EXCHANGE_TYPE.TAX_NORMAL,
                                                    resource_2=relations.RESOURCE_EXCHANGE_TYPE.NONE,
                                                    bill=None)

    def test_refresh_attributes__use_effects_from_storage(self):

        delta = 0.3

        tt_services.effects.cmd_debug_clear_service()

        self.p1.refresh_attributes()

        with self.check_delta(lambda: self.p1.attrs.sell_price, delta):
            effect = tt_api_effects.Effect(id=None,
                                           attribute=places_relations.ATTRIBUTE.SELL_PRICE,
                                           entity=self.p1.id,
                                           value=delta,
                                           name='test')
            tt_services.effects.cmd_register(effect)

            places_storage.effects.refresh()

            self.p1.refresh_attributes()

    def test_refresh_attributes__sync_map_storage_on_production_calculation(self):
        # тест проверяет, что при изменении радиуса влияния будет корректно пересчитано производство
        # это требует пересчёта карты, так как карта зависит от радиуса влияния (он определяет владение дорогами),
        # а дороги определяют траты на их поддержку
        # так как эффекты в процессе расчёта обрабатываются несколько раз, то в карте появляются неверные данные
        # (после сброса параметров радиусы влияния обнуляются и замараживаются в момент расчёта эффектов производства,
        #  которые не идут в расчёт, так как нужны только на следующем проходе).

        tt_services.effects.cmd_debug_clear_service()

        self.p1.attrs.size = 2
        self.p1.refresh_attributes()

        with self.check_not_changed(lambda: self.p1.attrs.production):
            self.p1.refresh_attributes()

        logic.register_effect(place_id=self.p1.id,
                              attribute=relations.ATTRIBUTE.CULTURE,
                              value=10.0,
                              name='test',
                              refresh_effects=True)

        with self.check_decreased(lambda: self.p1.attrs.production):
            self.p1.refresh_attributes()

    @mock.patch('the_tale.game.balance.constants.PLACE_STABILITY_PENALTY_FOR_RACES', 0)
    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    @mock.patch('the_tale.game.persons.objects.Person.get_economic_modifier', lambda obj, x: 10)
    @mock.patch('the_tale.game.roads.objects.Road.get_stabilization_price_for', lambda self, place: 33)
    def test_refresh_attributes__production(self):
        self.p1.set_modifier(modifiers.CITY_MODIFIERS.CRAFT_CENTER)
        self.p1.attrs.size = 3
        self.p1.attrs.power_economic = 6
        self.p1.attrs.money_economic = 4
        self.p1.attrs.area = 100

        self._create_test_exchanges()

        prototypes.ResourceExchangePrototype.create(place_1=self.p2,
                                                    place_2=self.p1,
                                                    resource_1=relations.RESOURCE_EXCHANGE_TYPE.NONE,
                                                    resource_2=relations.RESOURCE_EXCHANGE_TYPE.TRANSPORT_SMALL,
                                                    bill=None)

        self.p2.attrs.size = 3

        self.p1.refresh_attributes()

        place_1_2_distance = navigation_logic.manhattan_distance(self.p1.x, self.p1.y, self.p2.x, self.p2.y)
        place_1_3_distance = navigation_logic.manhattan_distance(self.p1.x, self.p1.y, self.p3.x, self.p3.y)

        expected_production = (0.33 * self.p1.attrs.power_economic * c.PLACE_GOODS_BONUS +
                               0.33 * self.p1.attrs.money_economic * c.PLACE_GOODS_BONUS +
                               0.34 * self.p1.area_size_equivalent * c.PLACE_GOODS_BONUS +
                               10 * len(self.p1.persons) +
                               - 3 * c.PLACE_GOODS_BONUS +  # place size support
                               c.PLACE_GOODS_BONUS +  # craft center
                               - relations.RESOURCE_EXCHANGE_TYPE.PRODUCTION_SMALL.amount +
                               relations.RESOURCE_EXCHANGE_TYPE.PRODUCTION_LARGE.amount +
                               - c.CELL_STABILIZATION_PRICE +  # place terrain supporte

                               # production exchanged, when place_1 is first place in exchange
                               # - c.RESOURCE_EXCHANGE_COST_PER_CELL * place_1_2_distance +
                               # - c.RESOURCE_EXCHANGE_COST_PER_CELL * place_1_3_distance +

                               # production exchanged, when place_1 is second place in exchange
                               - c.RESOURCE_EXCHANGE_COST_PER_CELL * place_1_2_distance +
                               - 33)  # roads support

        self.assertAlmostEqual(self.p1.attrs.production, expected_production)

    @mock.patch('the_tale.game.balance.constants.PLACE_STABILITY_PENALTY_FOR_RACES', 0)
    @mock.patch('the_tale.game.balance.constants.PLACE_STABILITY_PENALTY_FOR_MASTER', 0)
    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    @mock.patch('the_tale.game.persons.objects.Person.get_economic_modifier', lambda obj, x: 0.03)
    def test_refresh_attributes__safety(self):
        self.p1.set_modifier(modifiers.CITY_MODIFIERS.FORT)

        self._create_test_exchanges()

        self.p1.refresh_attributes()

        expected_safety = (0.03 * len(self.p1.persons) +
                           0.05 -
                           relations.RESOURCE_EXCHANGE_TYPE.SAFETY_SMALL.amount +
                           relations.RESOURCE_EXCHANGE_TYPE.SAFETY_LARGE.amount)

        self.assertAlmostEqual(self.p1.attrs.safety, expected_safety)

    @mock.patch('the_tale.game.balance.constants.PLACE_STABILITY_PENALTY_FOR_RACES', 0)
    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    @mock.patch('the_tale.game.persons.objects.Person.get_economic_modifier', lambda obj, x: 100)
    def test_refresh_attributes__transport(self):
        self.p1.set_modifier(modifiers.CITY_MODIFIERS.TRANSPORT_NODE)

        self.create_effect(self.p1.id, value=1000, attribute=relations.ATTRIBUTE.TRANSPORT)

        self._create_test_exchanges()

        self.p1.refresh_attributes()

        expected_transport = (1000 +
                              100 * len(self.p1.persons) +
                              0.2 -
                              relations.RESOURCE_EXCHANGE_TYPE.TRANSPORT_SMALL.amount +
                              relations.RESOURCE_EXCHANGE_TYPE.TRANSPORT_LARGE.amount -
                              c.TRANSPORT_FROM_PLACE_SIZE_PENALTY * self.p1.attrs.size)

        self.assertAlmostEqual(self.p1.attrs.transport, expected_transport)

    @mock.patch('the_tale.game.balance.constants.PLACE_STABILITY_PENALTY_FOR_RACES', 0)
    def test_refresh_attributes__culture__min_value(self):
        self.create_effect(self.p1.id, value=-1000, attribute=relations.ATTRIBUTE.CULTURE)

        self._create_test_exchanges()

        self.p1.refresh_attributes()

        self.assertTrue(-0.001 < self.p1.attrs.culture - c.PLACE_MIN_CULTURE < 0.001)

    def test_tax_order_equal_to_production_order(self):
        # необходимо, чтобы корректно работали эффекты аттрибута tax_size_border
        self.assertEqual(relations.ATTRIBUTE.PRODUCTION.order,
                         relations.ATTRIBUTE.TAX.order)

    @mock.patch('the_tale.game.balance.constants.PLACE_STABILITY_PENALTY_FOR_RACES', 0)
    def test_refresh_attributes__tax(self):

        # compensate low production
        self.create_effect(self.p1.id, value=10000, attribute=relations.ATTRIBUTE.PRODUCTION)
        self.p1.refresh_attributes()

        self._create_test_exchanges()

        self.assertEqual(self.p1.attrs.tax, 0)

        self.p1.refresh_attributes()

        self.assertEqual(self.p1.attrs.tax, 0.1)

    @mock.patch('the_tale.game.balance.constants.PLACE_STABILITY_PENALTY_FOR_RACES', 0)
    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    @mock.patch('the_tale.game.persons.objects.Person.get_economic_modifier', lambda obj, x: 100)
    def test_refresh_attributes__freedom(self):
        self.p1.set_modifier(modifiers.CITY_MODIFIERS.POLIC)
        self.create_effect(self.p1.id, value=1000, attribute=relations.ATTRIBUTE.FREEDOM)

        self._create_test_exchanges()

        self.p1.refresh_attributes()

        self.assertTrue(-0.001 < self.p1.attrs.freedom - (1000 + 100 * len(self.p1.persons) + 1.0 + 0.1) < 0.001)

    def test_refresh_attributes__freedom__min_value(self):
        self.create_effect(self.p1.id, value=-1000, attribute=relations.ATTRIBUTE.FREEDOM)

        self._create_test_exchanges()

        self.p1.refresh_attributes()

        self.assertTrue(-0.001 < self.p1.attrs.freedom - c.PLACE_MIN_FREEDOM < 0.001)

    @mock.patch('the_tale.game.balance.constants.PLACE_STABILITY_PENALTY_FOR_RACES', 0)
    @mock.patch('the_tale.game.balance.constants.PLACE_STABILITY_PENALTY_FOR_MASTER', 0)
    @mock.patch('the_tale.game.persons.objects.Person.get_economic_modifier', lambda obj, x: -0.05)
    def test_refresh_attributes__stability(self):
        self.create_effect(self.p1.id, value=-0.5, attribute=relations.ATTRIBUTE.STABILITY)
        self.create_effect(self.p1.id, value=0.25, attribute=relations.ATTRIBUTE.STABILITY)

        self.p1.refresh_attributes()

        self.assertTrue(-0.001 < self.p1.attrs.stability - (1.0 - 0.5 + 0.25 - 0.05 * len(self.p1.persons)) < 0.001)

    def test_refresh_attributes__stability__minimum(self):

        self.create_effect(self.p1.id, value=-0.6, attribute=relations.ATTRIBUTE.STABILITY)
        self.create_effect(self.p1.id, value=-0.55, attribute=relations.ATTRIBUTE.STABILITY)

        self.p1.refresh_attributes()

        self.assertTrue(-0.001 < self.p1.attrs.stability - c.PLACE_MIN_STABILITY < 0.001)

    def test_refresh_attributes__stability_maximum(self):
        self.create_effect(self.p1.id, value=0.6, attribute=relations.ATTRIBUTE.STABILITY)
        self.create_effect(self.p1.id, value=0.55, attribute=relations.ATTRIBUTE.STABILITY)

        self.p1.refresh_attributes()

        self.assertEqual(self.p1.attrs.stability, 1.0)

    def test_refresh_attributes__production__min_value(self):
        self.p1.attrs.size = 1
        self.p1.attrs.goods = 1000
        self.p1.refresh_attributes()

        old_production = self.p1.attrs.production
        old_tax = self.p1.attrs.tax

        self.create_effect(self.p1.id, value=-500, attribute=relations.ATTRIBUTE.PRODUCTION)

        self.p1.attrs.goods = 0

        self.p1.refresh_attributes()

        self.assertTrue(-0.001 < self.p1.attrs.production < 0.001)

        self.assertAlmostEqual(self.p1.attrs.tax, old_tax + abs(old_production - 500) * c.PLACE_TAX_PER_ONE_GOODS)

    def test_refresh_attributes__production__min_value__not_min_size(self):
        self.create_effect(self.p1.id, value=-1000, attribute=relations.ATTRIBUTE.PRODUCTION)
        self.p1.attrs.size = 10
        self.p1.attrs.goods = 0

        self.p1.refresh_attributes()

        self.assertTrue(self.p1.attrs.production < 0)

        self.assertEqual(self.p1.attrs.tax, 0)

    def test_refresh_attributes__tax_size_border__max_allowed_production(self):
        self.p1.attrs.size = 7
        self.p1.attrs.goods = 1000
        self.p1.attrs.set_tax_size_border(7)

        self.p1.refresh_attributes()

        old_production = self.p1.attrs.production

        self.assertTrue(old_production < 0)

        self.assertEqual(self.p1.attrs.tax, 0)

        self.p1.attrs.goods = 0

        self.p1.refresh_attributes()

        self.assertAlmostEqual(self.p1.attrs.production, old_production + c.MAX_PRODUCTION_FROM_TAX)

        self.assertAlmostEqual(self.p1.attrs.tax, c.MAX_PRODUCTION_FROM_TAX * c.PLACE_TAX_PER_ONE_GOODS)

    def test_refresh_attributes__tax_size_border__medium_production(self):
        self.p1.attrs.size = 7
        self.p1.attrs.goods = 1000
        self.p1.attrs.set_tax_size_border(7)

        self.p1.refresh_attributes()

        self.create_effect(self.p1.id, value=-self.p1.attrs.production, attribute=relations.ATTRIBUTE.PRODUCTION)
        self.p1.refresh_attributes()

        self.assertAlmostEqual(self.p1.attrs.production, 0)
        self.assertEqual(self.p1.attrs.tax, 0)

        test_production = 120

        self.create_effect(self.p1.id, value=-test_production, attribute=relations.ATTRIBUTE.PRODUCTION)

        self.p1.refresh_attributes()

        self.assertAlmostEqual(self.p1.attrs.production, -test_production)

        self.p1.attrs.goods = 0
        self.p1.refresh_attributes()

        self.assertAlmostEqual(self.p1.attrs.production, 0)

        self.assertAlmostEqual(self.p1.attrs.tax, 120 * c.PLACE_TAX_PER_ONE_GOODS)

    def test_refresh_attributes__tax_size_border__lower_size_with_positive_production(self):
        self.p1.attrs.size = 7
        self.p1.attrs.goods = 1000
        self.p1.attrs.set_tax_size_border(7)

        self.p1.refresh_attributes()

        self.create_effect(self.p1.id, value=-self.p1.attrs.production , attribute=relations.ATTRIBUTE.PRODUCTION)
        self.p1.refresh_attributes()

        self.assertAlmostEqual(self.p1.attrs.production, 0)
        self.assertEqual(self.p1.attrs.tax, 0)

        test_production = 120

        self.create_effect(self.p1.id, value=-test_production, attribute=relations.ATTRIBUTE.PRODUCTION)

        self.p1.refresh_attributes()

        self.assertAlmostEqual(self.p1.attrs.production, -test_production)

        self.p1.attrs.size = 6
        self.p1.attrs.goods = 0

        self.p1.refresh_attributes()

        self.assertAlmostEqual(self.p1.attrs.production, -test_production + c.PLACE_GOODS_BONUS + c.MAX_PRODUCTION_FROM_TAX)

        self.assertAlmostEqual(self.p1.attrs.tax, c.PLACE_TAX_PER_ONE_GOODS * c.MAX_PRODUCTION_FROM_TAX)

    @mock.patch('the_tale.game.persons.objects.Person.place_effects', lambda obj: [])
    def test_refresh_attributes__stability_penalty_for_masters_number(self):

        self.p1.attrs.size = 7
        self.p1.refresh_attributes()

        expected_max_persons = c.PLACE_MAX_PERSONS[self.p1.attrs.size]

        with self.check_not_changed(lambda: self.p1.attrs.stability):
            while len(self.p1.persons) < expected_max_persons:
                person = random.choice(list(persons_storage.persons.all()))
                persons_logic.move_person_to_place(person, self.p1)

            self.p1.refresh_attributes()

        with self.check_delta(lambda: round(self.p1.attrs.stability, 2), -0.15000000000000002):
            while len(self.p1.persons) <= expected_max_persons:
                person = random.choice(list(persons_storage.persons.all()))
                persons_logic.move_person_to_place(person, self.p1)

            self.p1.refresh_attributes()

    @mock.patch('the_tale.game.persons.objects.Person.place_effects', lambda obj: [])
    def test_refresh_attributes__stability_penalty_for_race_discrimination(self):
        self.p1.race = self.p1.races.dominant_race

        self.p1.refresh_attributes()

        with self.check_not_changed(lambda: self.p1.attrs.stability):
            self.p1.refresh_attributes()

        with self.check_not_changed(lambda: self.p1.attrs.stability):
            self.p1.race = game_relations.RACE.random(exclude=(self.p1.race,))
            self.p1.refresh_attributes()

        with self.check_delta(lambda: round(self.p1.attrs.stability, 2), -0.09999999999999998):
            self.p1.races._races[self.p1.races.dominant_race] += 0.1
            self.p1.races._races[self.p1.race] -= 0.1
            self.p1.refresh_attributes()

    @mock.patch('the_tale.game.persons.objects.Person.place_effects', lambda obj: [])
    def test_refresh_attributes__stability_penalty_for_wrong_specialization(self):
        self.p1.refresh_attributes()

        with self.check_not_changed(lambda: self.p1.attrs.stability):
            self.p1.set_modifier(modifiers.CITY_MODIFIERS.TRADE_CENTER)
            self.create_effect(self.p1.id, value=100, attribute=relations.ATTRIBUTE.MODIFIER_TRADE_CENTER)
            self.p1.refresh_attributes()

        with self.check_delta(lambda: self.p1.attrs.stability, -0.5):
            self.p1.attrs.modifier_trade_center = 0
            storage.effects.clear()
            self.p1.refresh_attributes()

    def test_refresh_attributes__stability__parameters_descreased(self):

        self._create_test_exchanges()
        self.p1.attrs.size = 5
        self.p1.refresh_attributes()

        self.create_effect(self.p1.id, value=-1.0, attribute=relations.ATTRIBUTE.STABILITY)

        with self.check_decreased(lambda: self.p1.attrs.production):
            with self.check_increased(lambda: self.p1.attrs.freedom):
                with self.check_decreased(lambda: self.p1.attrs.transport):
                    with self.check_decreased(lambda: self.p1.attrs.safety):
                        self.p1.refresh_attributes()

    def test_habit_change_speed(self):
        self.assertEqual(objects.Place._habit_change_speed(0, 100, 100), 0)
        self.assertEqual(objects.Place._habit_change_speed(0, 100, -100), 0)
        self.assertEqual(objects.Place._habit_change_speed(0, -100, 100), 0)

        self.assertEqual(objects.Place._habit_change_speed(0, 100, 0), c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM)
        self.assertEqual(objects.Place._habit_change_speed(0, 0, 100), -c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM)
        self.assertEqual(objects.Place._habit_change_speed(0, -100, 0), c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM)
        self.assertEqual(objects.Place._habit_change_speed(0, 0, -100), -c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM)
        self.assertEqual(objects.Place._habit_change_speed(0, 100, 1), c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM)
        self.assertEqual(objects.Place._habit_change_speed(0, -100, 1), c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM)
        self.assertEqual(objects.Place._habit_change_speed(0, 1, 100), -c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM)
        self.assertEqual(objects.Place._habit_change_speed(0, -1, 100), -c.PLACE_HABITS_CHANGE_SPEED_MAXIMUM)

    def test_habit_change_speed__penaltuy(self):
        self.assertEqual(objects.Place._habit_change_speed(0, 0, 0), 0)
        self.assertEqual(objects.Place._habit_change_speed(500, 0, 0), -5)
        self.assertEqual(objects.Place._habit_change_speed(-500, 0, 0), 5)


class BuildingTests(utils_testcase.TestCase):

    def setUp(self):
        super(BuildingTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_create(self):
        self.assertEqual(models.Building.objects.all().count(), 0)

        old_version = storage.buildings.version

        name = game_names.generator().get_test_name(name='building-name')

        building = logic.create_building(self.place_1.persons[0], utg_name=name)

        self.assertNotEqual(old_version, storage.buildings.version)

        self.assertEqual(models.Building.objects.all().count(), 1)

        old_version = storage.buildings.version

        name_2 = game_names.generator().get_test_name(name='building-name-2')
        building_2 = logic.create_building(self.place_1.persons[0], utg_name=name_2)

        self.assertEqual(old_version, storage.buildings.version)
        self.assertEqual(models.Building.objects.all().count(), 1)
        self.assertEqual(hash(building), hash(building_2))
        self.assertEqual(building.utg_name, name)

    def test_create_after_destroy(self):
        self.assertEqual(models.Building.objects.all().count(), 0)

        old_version = storage.buildings.version

        person = self.place_1.persons[0]

        name = game_names.generator().get_test_name(name='building-name')
        building = logic.create_building(person, utg_name=name)
        logic.destroy_building(building)

        name_2 = game_names.generator().get_test_name(name='building-name-2')
        building = logic.create_building(person, utg_name=name_2)

        self.assertNotEqual(old_version, storage.buildings.version)

        self.assertEqual(models.Building.objects.all().count(), 1)
        self.assertEqual(building.utg_name, name_2)

    def test_save__update_storage(self):
        building = logic.create_building(self.place_1.persons[0], utg_name=game_names.generator().get_test_name(name='building-name'))

        old_version = storage.buildings.version
        logic.save_building(building)
        self.assertNotEqual(old_version, storage.buildings.version)

    def test_destroy__update_storage(self):
        building = logic.create_building(self.place_1.persons[0], utg_name=game_names.generator().get_test_name(name='building-name'))

        old_version = storage.buildings.version
        logic.destroy_building(building)
        self.assertNotEqual(old_version, storage.buildings.version)
        self.assertFalse(building.id in storage.buildings)
