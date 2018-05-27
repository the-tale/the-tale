
from unittest import mock

from utg import words as utg_words
from utg import relations as utg_relations

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map
from the_tale.game import turn
from the_tale.game import names

from the_tale.game import tt_api_impacts

from the_tale.game.jobs import logic as jobs_logic
from the_tale.game.jobs import effects as jobs_effects

from the_tale.game.balance import formulas as f
from the_tale.game.balance import constants as c

from the_tale.game.places import relations as places_relations
from the_tale.game.places import logic as places_logic

from the_tale.game.politic_power import conf as politic_power_conf

from .. import logic
from .. import models
from .. import storage
from .. import relations
from .. import exceptions


FAKE_ECONOMIC = {places_relations.ATTRIBUTE.PRODUCTION: 1.0,
                 places_relations.ATTRIBUTE.FREEDOM: 0,
                 places_relations.ATTRIBUTE.SAFETY: 0.6,
                 places_relations.ATTRIBUTE.TRANSPORT: -0.4,
                 places_relations.ATTRIBUTE.STABILITY: 0.2,
                 places_relations.ATTRIBUTE.CULTURE: 0.7}


class LogicTests(testcase.TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()

        self.place_1, self.place_2, self.place_3 = create_test_map()

    def test_create_social_connection(self):
        connection_type = relations.SOCIAL_CONNECTION_TYPE.random()
        person_1 = self.place_1.persons[0]
        person_2 = self.place_2.persons[0]

        with self.check_delta(models.SocialConnection.objects.count, 1):
            with self.check_changed(lambda: storage.social_connections._version):
                connection = logic.create_social_connection(connection_type=connection_type, person_1=person_1, person_2=person_2)

        self.assertEqual(connection.connection, connection_type)
        self.assertTrue(person_1.id < person_2.id)
        self.assertEqual(connection.person_1_id, person_1.id)
        self.assertEqual(connection.person_2_id, person_2.id)

        self.assertIn(connection.id, storage.social_connections)

    def test_create_social_connection__uniqueness(self):
        connection = relations.SOCIAL_CONNECTION_TYPE.random()
        person_1 = self.place_1.persons[0]
        person_2 = self.place_2.persons[0]

        logic.create_social_connection(connection_type=connection, person_1=person_1, person_2=person_2)

        self.assertRaises(exceptions.PersonsAlreadyConnectedError, logic.create_social_connection, connection_type=connection, person_1=person_1, person_2=person_2)
        self.assertRaises(exceptions.PersonsAlreadyConnectedError, logic.create_social_connection, connection_type=connection, person_1=person_2, person_2=person_1)
        self.assertRaises(exceptions.PersonsAlreadyConnectedError, logic.create_social_connection, connection_type=relations.SOCIAL_CONNECTION_TYPE.random(exclude=(connection,)),
                          person_1=person_1, person_2=person_2)
        self.assertRaises(exceptions.PersonsAlreadyConnectedError, logic.create_social_connection, connection_type=relations.SOCIAL_CONNECTION_TYPE.random(exclude=(connection,)),
                          person_1=person_2, person_2=person_1)

    def test_remove_social_connection(self):
        connection_type = relations.SOCIAL_CONNECTION_TYPE.random()
        person_1 = self.place_1.persons[0]
        person_2 = self.place_2.persons[0]

        with self.check_delta(models.SocialConnection.objects.count, 1):
            with self.check_changed(lambda: storage.social_connections._version):
                connection = logic.create_social_connection(connection_type=connection_type, person_1=person_1, person_2=person_2)

        logic.remove_connection(connection)

        self.assertNotIn(connection.id, storage.social_connections)

    def test_move_person_to_place(self):
        person = self.place_1.persons[0]

        self.assertEqual(person.moved_at_turn, 0)

        turn.increment()
        turn.increment()
        turn.increment()

        with self.check_changed(lambda: storage.persons.version):
            logic.move_person_to_place(person, self.place_3)

        self.assertEqual(person.moved_at_turn, 3)
        self.assertEqual(person.place.id, self.place_3.id)


class PersonJobTests(testcase.TestCase):

    def setUp(self):
        super(PersonJobTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.person = self.place_1.persons[0]

        tt_api_impacts.debug_clear_service()

        self.job = jobs_logic.create_job(logic.PersonJob)

    def test_static_values(self):
        self.assertEqual(self.job.ACTOR, 'person')
        self.assertTrue(self.job.ACTOR_TYPE.is_PERSON)
        self.assertTrue(self.job.POSITIVE_TARGET_TYPE.is_JOB_PERSON_POSITIVE)
        self.assertTrue(self.job.NEGATIVE_TARGET_TYPE.is_JOB_PERSON_NEGATIVE)
        self.assertEqual(self.job.NORMAL_POWER, f.normal_job_power(politic_power_conf.settings.PERSON_INNER_CIRCLE_SIZE))

    def test_load_power(self):
        with mock.patch('the_tale.game.politic_power.logic.get_job_power', mock.Mock(return_value=666)) as get_job_power:
            self.assertEqual(self.job.load_power(self.person.id), 666)

        get_job_power.assert_called_once_with(person_id=self.person.id)

    def test_load_inner_circle(self):
        with mock.patch('the_tale.game.politic_power.logic.get_inner_circle', mock.Mock(return_value=666)) as get_inner_circle:
            self.assertEqual(self.job.load_inner_circle(self.person.id), 666)

        get_inner_circle.assert_called_once_with(person_id=self.person.id)

    def test_get_job_power(self):
        with mock.patch('the_tale.game.politic_power.storage.PowerStorage.total_power_fraction',
                        lambda self, target_id: 0.5):
            self.person.attrs.job_power_bonus = 0
            self.assertEqual(self.job.get_job_power(self.person.id), 0.875)

    def test_get_job_power__power_bonus(self):
        with mock.patch('the_tale.game.politic_power.storage.PowerStorage.total_power_fraction',
                        lambda self, target_id: 0.5):
            self.person.attrs.job_power_bonus = 10
            self.assertEqual(self.job.get_job_power(self.person.id), 10.875)

    def test_get_project_name(self):
        name = self.person.utg_name.form(utg_words.Properties(utg_relations.CASE.GENITIVE))
        self.assertEqual(self.job.get_project_name(self.person.id), 'Проект Мастера {name}'.format(name=name))

    def test_get_objects(self):
        self.assertEqual(self.job.get_objects(self.person.id),
                         {'person': self.person,
                          'place': self.person.place})

    @mock.patch('the_tale.game.persons.objects.Person.economic_attributes', FAKE_ECONOMIC)
    def test_job_effects_priorities(self):
        self.person.attrs.job_group_priority = {}
        self.assertEqual(self.person.job.get_effects_priorities(self.person.id),
                         {jobs_effects.EFFECT.PLACE_PRODUCTION: 1.0,
                          jobs_effects.EFFECT.PLACE_SAFETY: 0.6,
                          jobs_effects.EFFECT.PLACE_CULTURE: 0.7,
                          jobs_effects.EFFECT.PLACE_STABILITY: 0.2,
                          jobs_effects.EFFECT.HERO_MONEY: 0.3,
                          jobs_effects.EFFECT.HERO_ARTIFACT: 0.3,
                          jobs_effects.EFFECT.HERO_EXPERIENCE: 0.3,
                          jobs_effects.EFFECT.HERO_ENERGY: 0.3})

    @mock.patch('the_tale.game.persons.objects.Person.economic_attributes', FAKE_ECONOMIC)
    def test_job_effects_priorities__job_group_priorities(self):
        self.person.attrs.job_group_priority = {jobs_effects.EFFECT_GROUP.ON_PLACE: 0.5,
                                                jobs_effects.EFFECT_GROUP.ON_HEROES: 1.5}
        self.assertEqual(self.person.job.get_effects_priorities(self.person.id),
                         {jobs_effects.EFFECT.PLACE_PRODUCTION: 1.5,
                          jobs_effects.EFFECT.PLACE_SAFETY: 1.1,
                          jobs_effects.EFFECT.PLACE_CULTURE: 1.2,
                          jobs_effects.EFFECT.PLACE_STABILITY: 0.7,
                          jobs_effects.EFFECT.PLACE_TRANSPORT: 0.09999999999999998,
                          jobs_effects.EFFECT.PLACE_FREEDOM: 0.5,
                          jobs_effects.EFFECT.HERO_MONEY: 1.8,
                          jobs_effects.EFFECT.HERO_ARTIFACT: 1.8,
                          jobs_effects.EFFECT.HERO_EXPERIENCE: 1.8,
                          jobs_effects.EFFECT.HERO_ENERGY: 1.8})


class TTPowerImpactsTests(testcase.TestCase):

    def setUp(self):
        super(TTPowerImpactsTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()
        self.person = self.place_1.persons[-1]

        self.actor_type = tt_api_impacts.OBJECT_TYPE.random()
        self.actor_id = 666
        self.amount = 100500

    def test_person_inner_circle(self):
        impacts = list(logic.tt_power_impacts(person_inner_circle=True,
                                              place_inner_circle=False,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              person=self.person,
                                              amount=self.amount))

        self.assertCountEqual(impacts,
                              [tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.INNER_CIRCLE,
                                                          actor_type=self.actor_type,
                                                          actor_id=self.actor_id,
                                                          target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                          target_id=self.person.id,
                                                          amount=self.person.place.attrs.freedom * self.amount),
                              tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.JOB,
                                                         actor_type=self.actor_type,
                                                         actor_id=self.actor_id,
                                                         target_type=tt_api_impacts.OBJECT_TYPE.JOB_PERSON_POSITIVE,
                                                         target_id=self.person.id,
                                                         amount=self.person.place.attrs.freedom * self.amount),
                              tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.OUTER_CIRCLE,
                                                         actor_type=self.actor_type,
                                                         actor_id=self.actor_id,
                                                         target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                         target_id=self.person.place.id,
                                                         amount=self.person.place.attrs.freedom * self.amount)])

    def test_place_inner_circle(self):
        impacts = list(logic.tt_power_impacts(person_inner_circle=False,
                                              place_inner_circle=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              person=self.person,
                                              amount=self.amount))

        self.assertCountEqual(impacts,
                              [tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.OUTER_CIRCLE,
                                                          actor_type=self.actor_type,
                                                          actor_id=self.actor_id,
                                                          target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                          target_id=self.person.id,
                                                          amount=self.person.place.attrs.freedom * self.amount),
                              tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.JOB,
                                                         actor_type=self.actor_type,
                                                         actor_id=self.actor_id,
                                                         target_type=tt_api_impacts.OBJECT_TYPE.JOB_PLACE_POSITIVE,
                                                         target_id=self.person.place.id,
                                                         amount=self.person.place.attrs.freedom * self.amount),
                              tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.INNER_CIRCLE,
                                                         actor_type=self.actor_type,
                                                         actor_id=self.actor_id,
                                                         target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                         target_id=self.person.place.id,
                                                         amount=self.person.place.attrs.freedom * self.amount)])

    def test_inner_circle(self):
        impacts = list(logic.tt_power_impacts(person_inner_circle=True,
                                              place_inner_circle=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              person=self.person,
                                              amount=self.amount))

        self.assertCountEqual(impacts,
                              [tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.INNER_CIRCLE,
                                                          actor_type=self.actor_type,
                                                          actor_id=self.actor_id,
                                                          target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                          target_id=self.person.id,
                                                          amount=self.person.place.attrs.freedom * self.amount),
                              tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.JOB,
                                                         actor_type=self.actor_type,
                                                         actor_id=self.actor_id,
                                                         target_type=tt_api_impacts.OBJECT_TYPE.JOB_PERSON_POSITIVE,
                                                         target_id=self.person.id,
                                                         amount=self.person.place.attrs.freedom * self.amount),
                              tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.JOB,
                                                         actor_type=self.actor_type,
                                                         actor_id=self.actor_id,
                                                         target_type=tt_api_impacts.OBJECT_TYPE.JOB_PLACE_POSITIVE,
                                                         target_id=self.person.place.id,
                                                         amount=self.person.place.attrs.freedom * self.amount),
                              tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.INNER_CIRCLE,
                                                         actor_type=self.actor_type,
                                                         actor_id=self.actor_id,
                                                         target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                         target_id=self.person.place.id,
                                                         amount=self.person.place.attrs.freedom * self.amount)])

    def test_outer_circle(self):
        impacts = list(logic.tt_power_impacts(person_inner_circle=False,
                                              place_inner_circle=False,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              person=self.person,
                                              amount=self.amount))

        self.assertCountEqual(impacts,
                              [tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.OUTER_CIRCLE,
                                                          actor_type=self.actor_type,
                                                          actor_id=self.actor_id,
                                                          target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                          target_id=self.person.id,
                                                          amount=self.person.place.attrs.freedom * self.amount),
                              tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.OUTER_CIRCLE,
                                                         actor_type=self.actor_type,
                                                         actor_id=self.actor_id,
                                                         target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                         target_id=self.person.place.id,
                                                         amount=self.person.place.attrs.freedom * self.amount)])

    def test_amount_below_zero(self):
        impacts = list(logic.tt_power_impacts(person_inner_circle=True,
                                              place_inner_circle=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              person=self.person,
                                              amount=-self.amount))

        self.assertCountEqual(impacts,
                              [tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.INNER_CIRCLE,
                                                          actor_type=self.actor_type,
                                                          actor_id=self.actor_id,
                                                          target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                          target_id=self.person.id,
                                                          amount=-self.person.place.attrs.freedom * self.amount),
                              tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.JOB,
                                                         actor_type=self.actor_type,
                                                         actor_id=self.actor_id,
                                                         target_type=tt_api_impacts.OBJECT_TYPE.JOB_PERSON_NEGATIVE,
                                                         target_id=self.person.id,
                                                         amount=abs(self.person.place.attrs.freedom * self.amount)),
                              tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.JOB,
                                                         actor_type=self.actor_type,
                                                         actor_id=self.actor_id,
                                                         target_type=tt_api_impacts.OBJECT_TYPE.JOB_PLACE_NEGATIVE,
                                                         target_id=self.person.place.id,
                                                         amount=abs(self.person.place.attrs.freedom * self.amount)),
                              tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.INNER_CIRCLE,
                                                         actor_type=self.actor_type,
                                                         actor_id=self.actor_id,
                                                         target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                         target_id=self.person.place.id,
                                                         amount=-self.person.place.attrs.freedom * self.amount)])

    @mock.patch('the_tale.game.places.objects.Building.logical_integrity', 0.75)
    def test_has_building(self):
        places_logic.create_building(self.person, utg_name=names.generator().get_test_name())

        impacts = list(logic.tt_power_impacts(person_inner_circle=True,
                                              place_inner_circle=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              person=self.person,
                                              amount=self.amount))

        multiplier = (1 + c.BUILDING_PERSON_POWER_BONUS * 0.75)

        self.assertCountEqual(impacts,
                              [tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.INNER_CIRCLE,
                                                          actor_type=self.actor_type,
                                                          actor_id=self.actor_id,
                                                          target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                          target_id=self.person.id,
                                                          amount=self.person.place.attrs.freedom * self.amount * multiplier),
                              tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.JOB,
                                                         actor_type=self.actor_type,
                                                         actor_id=self.actor_id,
                                                         target_type=tt_api_impacts.OBJECT_TYPE.JOB_PERSON_POSITIVE,
                                                         target_id=self.person.id,
                                                         amount=self.person.place.attrs.freedom * self.amount * multiplier),
                              tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.JOB,
                                                         actor_type=self.actor_type,
                                                         actor_id=self.actor_id,
                                                         target_type=tt_api_impacts.OBJECT_TYPE.JOB_PLACE_POSITIVE,
                                                         target_id=self.person.place.id,
                                                         amount=self.person.place.attrs.freedom * self.amount * multiplier),
                              tt_api_impacts.PowerImpact(type=tt_api_impacts.IMPACT_TYPE.INNER_CIRCLE,
                                                         actor_type=self.actor_type,
                                                         actor_id=self.actor_id,
                                                         target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                         target_id=self.person.place.id,
                                                         amount=self.person.place.attrs.freedom * self.amount * multiplier)])
