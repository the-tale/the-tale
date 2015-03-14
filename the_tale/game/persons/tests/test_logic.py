# coding: utf-8
import random

import mock

from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from the_tale.game.map.roads.storage import waymarks_storage

from the_tale.game.persons import models
from the_tale.game.persons import storage
from the_tale.game.persons import conf
from the_tale.game.persons import relations
from the_tale.game.persons import logic
from the_tale.game.persons import exceptions



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


    def test_create_social_connection__from_one_place(self):
        connection = relations.SOCIAL_CONNECTION_TYPE.random()
        person_1 = self.place_1.persons[0]
        person_2 = self.place_1.persons[1]

        self.assertRaises(exceptions.PersonsFromOnePlaceError, logic.create_social_connection, connection_type=connection, person_1=person_1, person_2=person_2)


    def test_search_available_connections(self):
        # check if distances between places not changed
        distance_1_2 = waymarks_storage.look_for_road(self.place_1, self.place_2).length
        distance_2_3 = waymarks_storage.look_for_road(self.place_2, self.place_3).length

        self.assertTrue(distance_2_3 <
                        distance_1_2 <
                        waymarks_storage.look_for_road(self.place_1, self.place_3).length)

        # check that every place has more then 1 person
        self.assertTrue(len(self.place_1.persons) > 1)
        self.assertTrue(len(self.place_2.persons) > 1)
        self.assertTrue(len(self.place_3.persons) > 1)

        self.assertEqual(len(self.place_3.persons), 3)
        connected_persons = self.place_3.persons[1]

        test_person = self.place_2.persons[0]

        logic.create_social_connection(connection_type=relations.SOCIAL_CONNECTION_TYPE.random(), person_1=test_person, person_2=connected_persons)

        expected_persons = set(person.id for person in self.place_3.persons) - set((connected_persons.id,))

        person_out_game = self.place_3.add_person()
        person_out_game.move_out_game()
        person_removed = self.place_3.add_person()
        person_removed.remove_from_game()

        with mock.patch('the_tale.game.balance.constants.QUEST_AREA_RADIUS', (distance_1_2 + distance_2_3) / 2):
            candidates = set(person.id for person in logic.search_available_connections(test_person))

        # only ingame persons — no person_out_game and person_removed
        # no persons from same place — no persons from place_2
        # no persons out radius — no persons from place_1
        # no connected_persons — no connected_person
        self.assertEqual(expected_persons, candidates)


    def test_out_game_obsolete_connections(self):
        logic.create_missing_connections()

        out_gamed_person = random.choice(storage.persons_storage.filter(state=relations.PERSON_STATE.IN_GAME))

        out_gamed_connections_number = len(storage.social_connections.get_connected_persons_ids(out_gamed_person))

        with self.check_delta(lambda: len(storage.social_connections.all()), -out_gamed_connections_number):
            out_gamed_person.move_out_game()
            logic.out_game_obsolete_connections()

        self.assertEqual(models.SocialConnection.objects.filter(state=relations.SOCIAL_CONNECTION_STATE.OUT_GAME).count(),
                         out_gamed_connections_number)



    def test_create_missing_connections__success(self):
        with self.check_increased(models.SocialConnection.objects.count):
            with self.check_changed(lambda: storage.social_connections._version):
                logic.create_missing_connections()


    def test_create_missing_connections__minimum_connections(self):
        logic.create_missing_connections()

        for person in storage.persons_storage.filter(state=relations.PERSON_STATE.IN_GAME):
            self.assertTrue(len(storage.social_connections.get_connected_persons_ids(person)) >= conf.settings.SOCIAL_CONNECTIONS_MINIMUM)


    def test_create_missing_connections__restore_connections(self):
        logic.create_missing_connections()

        out_gamed_person = random.choice(storage.persons_storage.filter(state=relations.PERSON_STATE.IN_GAME))

        out_gamed_person.move_out_game()
        logic.out_game_obsolete_connections()

        logic.create_missing_connections()

        for person in storage.persons_storage.filter(state=relations.PERSON_STATE.IN_GAME):
            self.assertTrue(len(storage.social_connections.get_connected_persons_ids(person)) >= conf.settings.SOCIAL_CONNECTIONS_MINIMUM)
