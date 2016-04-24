# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.game.relations import RACE

from the_tale.game.logic import create_test_map
from the_tale.game.balance import constants as c

from the_tale.game.jobs import effects as jobs_effects

from the_tale.game import effects

from ..prototypes import ResourceExchangePrototype
from .. import relations
from .. import modifiers
from .. import objects


class PlaceTests(testcase.TestCase):

    def setUp(self):
        super(PlaceTests, self).setUp()
        self.p1, self.p2, self.p3 = create_test_map()

    @mock.patch('the_tale.game.balance.constants.PLACE_NEW_PLACE_LIVETIME', 0)
    def test_is_new__false(self):
        self.assertFalse(self.p1.is_new)

    @mock.patch('the_tale.game.balance.constants.PLACE_NEW_PLACE_LIVETIME', 60)
    def test_is_new__true(self):
        self.assertTrue(self.p1.is_new)

    def test_sync_race_no_signal_when_race_not_changed(self):
        with mock.patch('the_tale.game.places.races.Races.dominant_race', self.p1.race):
            with mock.patch('the_tale.game.places.signals.place_race_changed.send') as signal_counter:
                self.p1.sync_race()

        self.assertEqual(signal_counter.call_count, 0)

    def test_sync_race_signal_when_race_changed(self):
        new_race = None
        for race in RACE.records:
            if self.p1.race != race:
                new_race = race
                break

        with mock.patch('the_tale.game.places.races.Races.dominant_race', new_race):
            with mock.patch('the_tale.game.places.signals.place_race_changed.send') as signal_counter:
                self.p1.sync_race()


        self.assertEqual(signal_counter.call_count, 1)

    def test_sync_size__keepers_goods(self):
        self.p1.attrs.keepers_goods = c.PLACE_GOODS_BONUS + 50
        self.p1.attrs.sync_size(2)
        self.assertEqual(self.p1.attrs.keepers_goods, 50)

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
        ResourceExchangePrototype.create(place_1=self.p1,
                                         place_2=self.p2,
                                         resource_1=relations.RESOURCE_EXCHANGE_TYPE.PRODUCTION_SMALL,
                                         resource_2=relations.RESOURCE_EXCHANGE_TYPE.NONE,
                                         bill=None)

        ResourceExchangePrototype.create(place_1=self.p1,
                                         place_2=self.p3,
                                         resource_1=relations.RESOURCE_EXCHANGE_TYPE.NONE,
                                         resource_2=relations.RESOURCE_EXCHANGE_TYPE.PRODUCTION_LARGE,
                                         bill=None)

        ResourceExchangePrototype.create(place_1=self.p1,
                                         place_2=self.p2,
                                         resource_1=relations.RESOURCE_EXCHANGE_TYPE.SAFETY_SMALL,
                                         resource_2=relations.RESOURCE_EXCHANGE_TYPE.NONE,
                                         bill=None)

        ResourceExchangePrototype.create(place_1=self.p1,
                                         place_2=self.p3,
                                         resource_1=relations.RESOURCE_EXCHANGE_TYPE.NONE,
                                         resource_2=relations.RESOURCE_EXCHANGE_TYPE.SAFETY_LARGE,
                                         bill=None)

        ResourceExchangePrototype.create(place_1=self.p1,
                                         place_2=self.p2,
                                         resource_1=relations.RESOURCE_EXCHANGE_TYPE.TRANSPORT_SMALL,
                                         resource_2=relations.RESOURCE_EXCHANGE_TYPE.NONE,
                                         bill=None)

        ResourceExchangePrototype.create(place_1=self.p1,
                                         place_2=self.p3,
                                         resource_1=relations.RESOURCE_EXCHANGE_TYPE.NONE,
                                         resource_2=relations.RESOURCE_EXCHANGE_TYPE.TRANSPORT_LARGE,
                                         bill=None)

        ResourceExchangePrototype.create(place_1=self.p1,
                                         place_2=None,
                                         resource_1=relations.RESOURCE_EXCHANGE_TYPE.TAX_NORMAL,
                                         resource_2=relations.RESOURCE_EXCHANGE_TYPE.NONE,
                                         bill=None)


    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    @mock.patch('the_tale.game.persons.objects.Person.get_economic_modifier', lambda obj, x: 10)
    @mock.patch('the_tale.game.balance.formulas.place_goods_production', lambda size: 100 if size < 5 else 1000)
    def test_refresh_attributes__production(self):
        self.p1.attrs.keepers_goods = 10000
        self.p1.set_modifier(modifiers.CITY_MODIFIERS.CRAFT_CENTER)
        self.p1.attrs.size = 1
        self.p1.attrs.power_economic = 6

        self._create_test_exchanges()

        self.p1.refresh_attributes()

        expected_production = (c.PLACE_GOODS_BONUS +
                               1000 -
                               100 +
                               10 * len(self.p1.persons) +
                               self.p1.attrs.get_next_keepers_goods_spend_amount() -
                               relations.RESOURCE_EXCHANGE_TYPE.PRODUCTION_SMALL.amount +
                               relations.RESOURCE_EXCHANGE_TYPE.PRODUCTION_LARGE.amount )

        self.assertTrue(-0.001 < self.p1.attrs.production - expected_production < 0.001)

    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    @mock.patch('the_tale.game.persons.objects.Person.get_economic_modifier', lambda obj, x: 100)
    def test_refresh_attributes__safety(self):
        self.p1.set_modifier(modifiers.CITY_MODIFIERS.FORT)

        self._create_test_exchanges()

        self.p1.refresh_attributes()

        expected_safety = (1.0 - c.BATTLES_PER_TURN +
                           100 * len(self.p1.persons) +
                           0.05 -
                           relations.RESOURCE_EXCHANGE_TYPE.SAFETY_SMALL.amount +
                           relations.RESOURCE_EXCHANGE_TYPE.SAFETY_LARGE.amount)

        self.assertTrue(-0.001 < self.p1.attrs.safety - expected_safety < 0.001)

    def test_refresh_attributes__safety__min_value(self):
        self.p1.effects.add(effects.Effect(name=u'test', attribute=relations.ATTRIBUTE.SAFETY, value=-1000))

        self._create_test_exchanges()

        self.p1.refresh_attributes()

        self.assertTrue(-0.001 < self.p1.attrs.safety - c.PLACE_MIN_SAFETY < 0.001)

    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    @mock.patch('the_tale.game.persons.objects.Person.get_economic_modifier', lambda obj, x: 100)
    def test_refresh_attributes__transport(self):
        self.p1.set_modifier(modifiers.CITY_MODIFIERS.TRANSPORT_NODE)
        self.p1.effects.add(effects.Effect(name=u'test', attribute=relations.ATTRIBUTE.TRANSPORT, value=1000))

        self._create_test_exchanges()

        self.p1.refresh_attributes()

        expected_transport = (1.0 +
                              1000 +
                              100 * len(self.p1.persons) +
                              0.2 -
                              relations.RESOURCE_EXCHANGE_TYPE.TRANSPORT_SMALL.amount +
                              relations.RESOURCE_EXCHANGE_TYPE.TRANSPORT_LARGE.amount -
                              c.TRANSPORT_FROM_PLACE_SIZE_PENALTY * self.p1.attrs.size)

        self.assertTrue(-0.001 < self.p1.attrs.transport - expected_transport < 0.001)


    def test_refresh_attributes__transport__min_value(self):
        self.p1.effects.add(effects.Effect(name=u'test', attribute=relations.ATTRIBUTE.TRANSPORT, value=-1000))

        self._create_test_exchanges()

        self.p1.refresh_attributes()

        self.assertTrue(-0.001 < self.p1.attrs.transport - c.PLACE_MIN_TRANSPORT < 0.001)


    def test_refresh_attributes__tax(self):

        self._create_test_exchanges()

        self.assertEqual(self.p1.attrs.tax, 0)

        self.p1.refresh_attributes()

        self.assertEqual(self.p1.attrs.tax, 0.05)

    @mock.patch('the_tale.game.places.objects.Place.is_modifier_active', lambda self: True)
    @mock.patch('the_tale.game.persons.objects.Person.get_economic_modifier', lambda obj, x: 100)
    def test_refresh_attributes__freedom(self):
        self.p1.set_modifier(modifiers.CITY_MODIFIERS.POLIC)
        self.p1.effects.add(effects.Effect(name=u'test', attribute=relations.ATTRIBUTE.FREEDOM, value=1000))

        self._create_test_exchanges()

        self.p1.refresh_attributes()

        self.assertTrue(-0.001 < self.p1.attrs.freedom - (1000 + 100 * len(self.p1.persons) + 1.0 + 0.1) < 0.001)


    @mock.patch('the_tale.game.persons.objects.Person.get_economic_modifier', lambda obj, x: -0.05)
    def test_refresh_attributes__stability(self):
        self.p1.effects.add(effects.Effect(name=u'test', attribute=relations.ATTRIBUTE.STABILITY, value=-0.5))
        self.p1.effects.add(effects.Effect(name=u'test', attribute=relations.ATTRIBUTE.STABILITY, value=0.25))

        self.p1.refresh_attributes()

        self.assertTrue(-0.001 < self.p1.attrs.stability - (1.0 - 0.5 + 0.25 - 0.05 * len(self.p1.persons)) < 0.001)


    def test_refresh_attributes__stability__minimum(self):

        self.p1.effects.add(effects.Effect(name=u'test', attribute=relations.ATTRIBUTE.STABILITY, value=-0.6))
        self.p1.effects.add(effects.Effect(name=u'test', attribute=relations.ATTRIBUTE.STABILITY, value=-0.55))

        self.p1.refresh_attributes()

        self.assertTrue(-0.001 < self.p1.attrs.stability - c.PLACE_MIN_STABILITY < 0.001)


    def test_refresh_attributes__stability_maximum(self):
        self.p1.effects.add(effects.Effect(name=u'test', attribute=relations.ATTRIBUTE.STABILITY, value=0.6))
        self.p1.effects.add(effects.Effect(name=u'test', attribute=relations.ATTRIBUTE.STABILITY, value=0.55))

        self.p1.refresh_attributes()

        self.assertEqual(self.p1.attrs.stability, 1.0)


    @mock.patch('the_tale.game.persons.objects.Person.get_economic_modifier', lambda obj, x: -0.05)
    def test_stability__reduce_effects(self):
        self.p1.effects.add(effects.Effect(name=u'x', attribute=relations.ATTRIBUTE.STABILITY, value=-0.5))
        self.p1.effects.add(effects.Effect(name=u'y', attribute=relations.ATTRIBUTE.STABILITY, value=0.25))

        self.p1.refresh_attributes()

        self.assertTrue(-0.001 < self.p1.attrs.stability - (0.75 - 0.05 * len(self.p1.persons)) < 0.001)

        self.p1.effects_update_step()

        self.assertEqual(len(self.p1.effects.effects), 2)

        for effect in self.p1.effects.effects:
            if effect.name == 'x':
                self.assertEqual(effect.value, -0.5 + c.PLACE_STABILITY_RECOVER_SPEED / 2)
            else:
                self.assertEqual(effect.value, 0.25 - c.PLACE_STABILITY_RECOVER_SPEED / 2)


    def test_stability__parameters_removed(self):
        self.p1.attrs.stability_renewing_speed = 0.25

        self.p1.effects.add(effects.Effect(name=u'x', attribute=relations.ATTRIBUTE.STABILITY, value=-0.5))
        self.p1.effects.add(effects.Effect(name=u'y', attribute=relations.ATTRIBUTE.STABILITY, value=0.25))

        self.p1.effects_update_step()
        self.assertEqual(len(self.p1.effects.effects), 2)

        self.p1.effects_update_step()
        self.assertEqual(len(self.p1.effects.effects), 1)

        self.assertEqual(self.p1.effects.effects[0].name, 'x')
        self.assertEqual(self.p1.effects.effects[0].value, -0.25)

        self.p1.effects_update_step()
        self.assertEqual(len(self.p1.effects.effects), 0)


    def test_refresh_attributes__stability__parameters_descreased(self):

        self._create_test_exchanges()
        self.p1.refresh_attributes()

        self.p1.effects.add(effects.Effect(name=u'x', attribute=relations.ATTRIBUTE.STABILITY, value=-1.0))

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


    def test_get_next_keepers_goods_spend_amount__0(self):
        self.assertEqual(self.p1.attrs.keepers_goods, 0)
        self.assertEqual(self.p1.attrs.get_next_keepers_goods_spend_amount(), 0)

    def test_get_next_keepers_goods_spend_amount__less_then_production(self):
        self.p1.attrs.keepers_goods = c.PLACE_GOODS_BONUS - 1
        self.assertEqual(self.p1.attrs.get_next_keepers_goods_spend_amount(), c.PLACE_GOODS_BONUS - 1)

    def test_get_next_keepers_goods_spend_amount__less_then_production_barrier(self):
        self.p1.attrs.keepers_goods = int((c.PLACE_GOODS_BONUS - 1) / c.PLACE_KEEPERS_GOODS_SPENDING)
        self.assertTrue(self.p1.attrs.keepers_goods > c.PLACE_GOODS_BONUS)
        self.assertEqual(self.p1.attrs.get_next_keepers_goods_spend_amount(), c.PLACE_GOODS_BONUS)

    def test_get_next_keepers_goods_spend_amount__greater_then_production(self):
        self.p1.attrs.keepers_goods = int((c.PLACE_GOODS_BONUS + 1) / c.PLACE_KEEPERS_GOODS_SPENDING)
        self.assertEqual(self.p1.attrs.get_next_keepers_goods_spend_amount(), c.PLACE_GOODS_BONUS + 1)


class PlaceJobsTests(testcase.TestCase):

    def setUp(self):
        super(PlaceJobsTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()


    def test_job_effects_priorities(self):
        self.assertEqual(self.place_1.job_effects_priorities(),
                         {effect: 1 for effect in jobs_effects.EFFECT.records})

    @mock.patch('the_tale.game.places.objects.Place.total_politic_power_fraction', 0.5)
    def test_get_job_power(self):
        self.assertEqual(self.place_1.get_job_power(), 1.5)


    def test_update_job(self):

        with self.check_not_changed(lambda: self.place_1.job.effect):
            with mock.patch('the_tale.game.jobs.effects.BaseEffect.apply_to_heroes') as apply_to_heroes:
                self.place_1.job.give_power(1)
                self.assertEqual(self.place_1.update_job(), ())

        self.assertEqual(apply_to_heroes.call_count, 0)

        with self.check_changed(lambda: self.place_1.job.effect):
            with mock.patch('the_tale.game.jobs.effects.BaseEffect.apply_to_heroes', mock.Mock(return_value=(1, 2))) as apply_to_heroes:
                self.place_1.job.give_power(1000000000)
                self.assertEqual(self.place_1.update_job(), (1, 2))

        self.assertEqual(apply_to_heroes.call_count, 1)
