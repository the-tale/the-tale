# coding: utf-8


from the_tale.common.utils import testcase

from the_tale.game.logic import create_test_map

from the_tale.game.persons import storage
from the_tale.game.persons import relations
from the_tale.game.persons import logic


class SocialConnectionsStorageTest(testcase.TestCase):

    def setUp(self):
        super(SocialConnectionsStorageTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.person_1_1, self.person_1_2 = self.place_1.persons[:2]
        self.person_2_1, self.person_2_2 = self.place_2.persons[:2]
        self.person_3_1, self.person_3_2 = self.place_3.persons[:2]

        self.connection_1 = logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.random(), self.person_1_1, self.person_2_1)
        self.connection_2 = logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.random(), self.person_1_2, self.person_2_1)
        self.connection_3 = logic.create_social_connection(relations.SOCIAL_CONNECTION_TYPE.random(), self.person_3_1, self.person_2_1)


    def test_state(self):
        self.assertEqual(len(storage.social_connections.all()), 3)
        self.assertEqual(storage.social_connections._person_connections, {self.person_1_1.id: {self.person_2_1.id: self.connection_1},
                                                                          self.person_1_2.id: {self.person_2_1.id: self.connection_2},
                                                                          self.person_3_1.id: {self.person_2_1.id: self.connection_3},
                                                                          self.person_2_1.id: {self.person_1_1.id: self.connection_1,
                                                                                               self.person_1_2.id: self.connection_2,
                                                                                               self.person_3_1.id: self.connection_3}})


    def test_out_game_connection(self):
        with self.check_delta(lambda: len(storage.social_connections.all()), -1):
            logic.remove_connection(self.connection_2)


    def test_get_connected_persons_ids(self):
        self.assertEqual(set(storage.social_connections.get_connected_persons_ids(self.person_1_1)),
                         set((self.person_2_1.id,)))
        self.assertEqual(set(storage.social_connections.get_connected_persons_ids(self.person_2_1)),
                         set((self.person_1_1.id, self.person_1_2.id, self.person_3_1.id)))


    def test_get_person_connections(self):
        self.assertEqual(set(storage.social_connections.get_person_connections(self.person_1_1)),
                         set(((self.connection_1.connection, self.person_2_1.id),)))
        self.assertEqual(set(storage.social_connections.get_person_connections(self.person_2_1)),
                         set(((self.connection_1.connection, self.person_1_1.id),
                              (self.connection_2.connection, self.person_1_2.id),
                              (self.connection_3.connection, self.person_3_1.id))))


    def test_is_connected(self):
        self.assertTrue(storage.social_connections.is_connected(self.person_3_1, self.person_2_1))
        self.assertTrue(storage.social_connections.is_connected(self.person_2_1, self.person_3_1))

        self.assertFalse(storage.social_connections.is_connected(self.person_3_1, self.person_1_1))
        self.assertFalse(storage.social_connections.is_connected(self.person_1_1, self.person_3_1))
