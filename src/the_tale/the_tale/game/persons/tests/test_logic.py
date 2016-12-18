# coding: utf-8

from unittest import mock

from the_tale.common.utils import testcase

from the_tale.game.balance import constants as c

from the_tale.game.logic import create_test_map
from the_tale.game.prototypes import TimePrototype

from the_tale.game.roads.storage import waymarks_storage

from the_tale.game.persons import models
from the_tale.game.persons import storage
from the_tale.game.persons import conf
from the_tale.game.persons import relations
from the_tale.game.persons import logic
from the_tale.game.persons import exceptions

from the_tale.linguistics import logic as linguistics_logic

from .. import logic
from .. import exceptions
from .. import storage


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

        game_time = TimePrototype.get_current_time()
        game_time.increment_turn()
        game_time.increment_turn()
        game_time.increment_turn()

        with self.check_changed(lambda: storage.persons.version):
            logic.move_person_to_place(person, self.place_3)

        self.assertEqual(person.moved_at_turn, 3)
        self.assertEqual(person.place.id, self.place_3.id)




class PersonPowerTest(testcase.TestCase):

    def setUp(self):
        super(PersonPowerTest, self).setUp()
        linguistics_logic.sync_static_restrictions()

        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.person = self.place_1.persons[0]


    def test_inner_circle_size(self):
        self.assertEqual(self.person.politic_power.INNER_CIRCLE_SIZE, 3)


    def test_initialization(self):
        self.assertEqual(self.person.total_politic_power_fraction, 0)


    @mock.patch('the_tale.game.places.attributes.Attributes.freedom', 0.5)
    def test_change_power(self):
        with mock.patch('the_tale.game.politic_power.PoliticPower.change_power') as change_power:
            self.assertEqual(self.person.politic_power.change_power(person=self.person,
                                                                    hero_id=None,
                                                                    has_in_preferences=False,
                                                                    power=1000),
                             1000)

        self.assertEqual(change_power.call_args,
                         mock.call(owner=self.person,
                                   hero_id=None,
                                   has_in_preferences=False,
                                   power=500))


    @mock.patch('the_tale.game.places.attributes.Attributes.freedom', 0.5)
    @mock.patch('the_tale.game.persons.objects.Person.has_building', True)
    def test_change_power__has_building(self):
        self.assertEqual(c.BUILDING_PERSON_POWER_BONUS, 0.25)

        with mock.patch('the_tale.game.politic_power.PoliticPower.change_power') as change_power:
            self.assertEqual(self.person.politic_power.change_power(person=self.person,
                                                                    hero_id=None,
                                                                    has_in_preferences=False,
                                                                    power=1000),
                             1250)

        self.assertEqual(change_power.call_args,
                         mock.call(owner=self.person,
                                   hero_id=None,
                                   has_in_preferences=False,
                                   power=625))
