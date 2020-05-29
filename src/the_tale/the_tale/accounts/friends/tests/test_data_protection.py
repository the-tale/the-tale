
import smart_imports

smart_imports.all()


class CollectDataTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.accounts = [self.accounts_factory.create_account() for _ in range(6)]

    def test_no_friends__collect(self):
        report = data_protection.collect_data(self.accounts[0].id)
        self.assertEqual(report, [])

    def test_no_friends__remove(self):
        data_protection.remove_data(self.accounts[0].id)

    def prepair_data(self):
        friendships = [prototypes.FriendshipPrototype.request_friendship(self.accounts[0], self.accounts[1], 'text 1'),
                       prototypes.FriendshipPrototype.request_friendship(self.accounts[0], self.accounts[2], 'text 2'),
                       prototypes.FriendshipPrototype.request_friendship(self.accounts[3], self.accounts[0], 'text 3'),
                       prototypes.FriendshipPrototype.request_friendship(self.accounts[4], self.accounts[0], 'text 4'),
                       prototypes.FriendshipPrototype.request_friendship(self.accounts[5], self.accounts[0], 'text 5'),
                       prototypes.FriendshipPrototype.request_friendship(self.accounts[1], self.accounts[2], 'text 6'),
                       prototypes.FriendshipPrototype.request_friendship(self.accounts[1], self.accounts[3], 'text 7')]

        friendships[0]._confirm()
        friendships[2]._confirm()

        prototypes.FriendshipPrototype.remove_friendship(self.accounts[4], self.accounts[0])

        friendships[6]._confirm()

        return friendships

    def test_has_friends__collect(self):
        friendships = self.prepair_data()

        report = data_protection.collect_data(self.accounts[0].id)

        self.assertCountEqual(report,
                              [('friendship', {'friend_1': self.accounts[0].id,
                                               'friend_2': self.accounts[1].id,
                                               'is_confirmed': True,
                                               'text': 'text 1',
                                               'created_at': friendships[0]._model.created_at}),
                               ('friendship', {'friend_1': self.accounts[0].id,
                                               'friend_2': self.accounts[2].id,
                                               'is_confirmed': False,
                                               'text': 'text 2',
                                               'created_at': friendships[1]._model.created_at}),
                               ('friendship', {'friend_1': self.accounts[3].id,
                                               'friend_2': self.accounts[0].id,
                                               'is_confirmed': True,
                                               'text': 'text 3',
                                               'created_at': friendships[2]._model.created_at}),
                               ('friendship', {'friend_1': self.accounts[5].id,
                                               'friend_2': self.accounts[0].id,
                                               'is_confirmed': False,
                                               'text': 'text 5',
                                               'created_at': friendships[4]._model.created_at})])

    def test_has_friends__remove(self):
        friendships = self.prepair_data()

        data_protection.remove_data(self.accounts[0].id)

        report = data_protection.collect_data(self.accounts[0].id)

        self.assertCountEqual(report, [])

        report = data_protection.collect_data(self.accounts[1].id)

        self.assertCountEqual(report,
                              [('friendship', {'friend_1': self.accounts[1].id,
                                               'friend_2': self.accounts[2].id,
                                               'is_confirmed': False,
                                               'text': 'text 6',
                                               'created_at': friendships[5]._model.created_at}),
                               ('friendship', {'friend_1': self.accounts[1].id,
                                               'friend_2': self.accounts[3].id,
                                               'is_confirmed': True,
                                               'text': 'text 7',
                                               'created_at': friendships[6]._model.created_at})])
