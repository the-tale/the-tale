
import smart_imports

smart_imports.all()


class PersonRemoveSocialConnectionTests(helpers.BaseTestPrototypes):

    def setUp(self):
        super(PersonRemoveSocialConnectionTests, self).setUp()

        self.person_1_1 = self.place1.persons[0]
        self.person_2_1, self.person_2_2 = self.place2.persons[0:2]
        self.person_3_1 = self.place3.persons[0]

        self.account = self.accounts_factory.create_account()

        politic_power_logic.add_power_impacts(persons_logic.tt_power_impacts(person_inner_circle=True,
                                                                             place_inner_circle=True,
                                                                             actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                             actor_id=self.account.id,
                                                                             person=self.person_1_1,
                                                                             amount=100,
                                                                             fame=0))
        politic_power_logic.add_power_impacts(persons_logic.tt_power_impacts(person_inner_circle=True,
                                                                             place_inner_circle=True,
                                                                             actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                             actor_id=self.account.id,
                                                                             person=self.person_2_2,
                                                                             amount=100,
                                                                             fame=0))

        persons_logic.create_social_connection(connection_type=persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER,
                                               person_1=self.person_1_1,
                                               person_2=self.person_2_1)

        self.bill_data = bills.person_remove_social_connection.PersonRemoveSocialConnection(person_1_id=self.person_1_1.id,
                                                                                            person_2_id=self.person_2_1.id)
        self.bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

    def test_create(self):
        self.assertEqual(self.bill.data.person_1_id, self.person_1_1.id)
        self.assertEqual(self.bill.data.person_2_id, self.person_2_1.id)
        self.assertEqual(self.bill.data.place_1_id, self.place1.id)
        self.assertEqual(self.bill.data.place_2_id, self.place2.id)
        self.assertEqual(self.bill.data.old_place_1_name, self.place1.utg_name)
        self.assertEqual(self.bill.data.old_place_2_name, self.place2.utg_name)
        self.assertTrue(self.bill.data.connection_type.is_PARTNER)

    def test_actors(self):
        self.assertEqual(set([id(a) for a in self.bill_data.actors]),
                         set([id(self.place1), id(self.place2), id(self.person_1_1), id(self.person_2_1)]))

    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_MIN_LIVE_TIME', 0)
    @mock.patch('the_tale.game.balance.constants.PERSON_MOVE_DELAY', 0)
    def test_update(self):

        persons_logic.create_social_connection(connection_type=persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER,
                                               person_1=self.person_2_2,
                                               person_2=self.person_3_1)

        data = {'caption': 'new-caption',
                'chronicle_on_accepted': 'new-chronicle-on-accepted',
                'person_1': self.person_2_2.id,
                'person_2': self.person_3_1.id}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)

        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = prototypes.BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.person_1_id, self.person_2_2.id)
        self.assertEqual(self.bill.data.person_2_id, self.person_3_1.id)
        self.assertEqual(self.bill.data.place_1_id, self.place2.id)
        self.assertEqual(self.bill.data.place_2_id, self.place3.id)
        self.assertEqual(self.bill.data.old_place_1_name, self.place2.utg_name)
        self.assertEqual(self.bill.data.old_place_2_name, self.place3.utg_name)

    def test_user_form__min_live_time(self):
        data = {'caption': 'caption-caption',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person_1': self.person_1_1.id,
                'person_2': self.person_2_1.id}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertFalse(form.is_valid())

    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_MIN_LIVE_TIME', 0)
    def test_user_form__has_no_connection(self):
        data = {'caption': 'caption-caption',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person_1': self.person_1_1.id,
                'person_2': self.person_2_2.id}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertFalse(form.is_valid())

    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_MIN_LIVE_TIME', 0)
    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_LIMIT', 1)
    def test_user_form__not_in_circles(self):
        data = {'caption': 'caption-caption',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person_1': self.person_2_2.id,
                'person_2': self.person_3_1.id}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertFalse(form.is_valid())

    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_MIN_LIVE_TIME', 0)
    def test_user_form__second_in_circle(self):
        data = {'caption': 'caption-caption',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person_1': self.person_2_1.id,
                'person_2': self.person_1_1.id}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertTrue(form.is_valid())

    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_MIN_LIVE_TIME', 0)
    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_apply(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        data = self.bill.user_form_initials
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form, self.account1)

        self.assertTrue(self.bill.apply())

        bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        self.assertFalse(persons_storage.social_connections.is_connected(self.person_1_1, self.person_2_1))

    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_MIN_LIVE_TIME', 0)
    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_LIMIT', 1)
    def test_has_meaning__no_connections(self):
        self.assertTrue(self.bill.has_meaning())
        connection = persons_storage.social_connections.get_connection(self.person_1_1, self.person_2_1)
        persons_logic.remove_connection(connection)
        self.assertFalse(self.bill.has_meaning())
