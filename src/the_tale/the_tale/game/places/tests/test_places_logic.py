
from unittest import mock

from utg import words as utg_words
from utg import relations as utg_relations

from the_tale.common.utils import testcase

from the_tale.game import names
from the_tale.game import tt_api_impacts

from the_tale.game.logic import create_test_map

from the_tale.game.map import conf as map_conf

from the_tale.game.jobs import logic as jobs_logic
from the_tale.game.jobs import effects as jobs_effects

from the_tale.game.balance import formulas as f

from the_tale.game.politic_power import conf as politic_power_conf

from .. import logic
from .. import storage


class GetAvailablePositionsTests(testcase.TestCase):

    def setUp(self):
        super(GetAvailablePositionsTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

    def test_get_available_positions(self):

        building = logic.create_building(self.place_1.persons[0], utg_name=names.generator().get_test_name(name='building-name'))

        positions = logic.get_available_positions(self.place_1.x, self.place_1.y)

        self.assertTrue(positions)

        for place in storage.places.all():
            self.assertFalse((place.x, place.y) in positions)

        for building in storage.buildings.all():
            self.assertFalse((building.x, building.y) in positions)

        for x, y in positions:
            self.assertTrue(0 <= x < map_conf.map_settings.WIDTH)
            self.assertTrue(0 <= y < map_conf.map_settings.HEIGHT)

    def test_dynamic_position_radius(self):
        with mock.patch('the_tale.game.balance.constants.BUILDING_POSITION_RADIUS', 2):
            positions = logic.get_available_positions(-3, -1)
            self.assertEqual(positions, set([(0, 0), (0, 1), (0, 2)]))

        with mock.patch('the_tale.game.balance.constants.BUILDING_POSITION_RADIUS', 2):
            positions = logic.get_available_positions(-4, -1)
            self.assertEqual(positions, set([(0, 0), (0, 1), (0, 2), (0, 3)]))


class TTPowerImpactsTests(testcase.TestCase):

    def setUp(self):
        super(TTPowerImpactsTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.actor_type = tt_api_impacts.OBJECT_TYPE.random()
        self.actor_id = 666
        self.amount = 100500

    def test_inner_circle(self):
        impacts = list(logic.tt_power_impacts(inner_circle=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              place=self.place_1,
                                              amount=self.amount))

        self.assertCountEqual(impacts,
                              [tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.INNER_CIRCLE,
                                                          actor_type=self.actor_type,
                                                          actor_id=self.actor_id,
                                                          target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                          target_id=self.place_1.id,
                                                          amount=self.place_1.attrs.freedom * self.amount),
                              tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.JOB,
                                                          actor_type=self.actor_type,
                                                          actor_id=self.actor_id,
                                                          target_type=tt_api_impacts.OBJECT_TYPE.JOB_PLACE_POSITIVE,
                                                          target_id=self.place_1.id,
                                                          amount=self.place_1.attrs.freedom * self.amount)])

    def test_outer_circle(self):
        impacts = list(logic.tt_power_impacts(inner_circle=False,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              place=self.place_1,
                                              amount=self.amount))

        self.assertCountEqual(impacts,
                              [tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.OUTER_CIRCLE,
                                                          actor_type=self.actor_type,
                                                          actor_id=self.actor_id,
                                                          target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                          target_id=self.place_1.id,
                                                          amount=self.place_1.attrs.freedom * self.amount)])

    def test_amount_below_zero(self):
        impacts = list(logic.tt_power_impacts(inner_circle=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              place=self.place_1,
                                              amount=-self.amount))

        self.assertCountEqual(impacts,
                              [tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.INNER_CIRCLE,
                                                          actor_type=self.actor_type,
                                                          actor_id=self.actor_id,
                                                          target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                          target_id=self.place_1.id,
                                                          amount=-self.place_1.attrs.freedom * self.amount),
                              tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.JOB,
                                                          actor_type=self.actor_type,
                                                          actor_id=self.actor_id,
                                                          target_type=tt_api_impacts.OBJECT_TYPE.JOB_PLACE_NEGATIVE,
                                                          target_id=self.place_1.id,
                                                          amount=abs(self.place_1.attrs.freedom * self.amount))])


class PlaceJobTests(testcase.TestCase):

    def setUp(self):
        super(PlaceJobTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        tt_api_impacts.debug_clear_service()

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
