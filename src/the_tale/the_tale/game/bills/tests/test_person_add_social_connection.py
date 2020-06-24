
import smart_imports

smart_imports.all()


class PersonAddSocialConnectionTests(helpers.BaseTestPrototypes):

    def setUp(self):
        super(PersonAddSocialConnectionTests, self).setUp()

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

        self.bill_data = bills.person_add_social_connection.PersonAddSocialConnection(person_1_id=self.person_1_1.id,
                                                                                      person_2_id=self.person_2_1.id,
                                                                                      connection_type=persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER)
        self.bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

    def test_create(self):
        self.assertEqual(self.bill.data.person_1_id, self.person_1_1.id)
        self.assertEqual(self.bill.data.person_2_id, self.person_2_1.id)
        self.assertTrue(self.bill.data.connection_type.is_PARTNER)
        self.assertEqual(self.bill.data.place_1_id, self.place1.id)
        self.assertEqual(self.bill.data.place_2_id, self.place2.id)
        self.assertEqual(self.bill.data.old_place_1_name, self.place1.utg_name)
        self.assertEqual(self.bill.data.old_place_2_name, self.place2.utg_name)

    def test_actors(self):
        self.assertEqual(set([id(a) for a in self.bill_data.actors]),
                         set([id(self.place1), id(self.place2), id(self.person_1_1), id(self.person_2_1)]))

    @mock.patch('the_tale.game.balance.constants.PERSON_MOVE_DELAY', 0)
    def test_update(self):
        data = {'caption': 'new-caption',
                'chronicle_on_accepted': 'new-chronicle-on-accepted',
                'person_1': self.person_2_2.id,
                'person_2': self.person_3_1.id,
                'connection_type': persons_relations.SOCIAL_CONNECTION_TYPE.CONCURRENT}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)

        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = prototypes.BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.person_1_id, self.person_2_2.id)
        self.assertEqual(self.bill.data.person_2_id, self.person_3_1.id)
        self.assertTrue(self.bill.data.connection_type.is_CONCURRENT)
        self.assertEqual(self.bill.data.place_1_id, self.place2.id)
        self.assertEqual(self.bill.data.place_2_id, self.place3.id)
        self.assertEqual(self.bill.data.old_place_1_name, self.place2.utg_name)
        self.assertEqual(self.bill.data.old_place_2_name, self.place3.utg_name)

    @mock.patch('the_tale.game.balance.constants.PERSON_MOVE_DELAY', 1)
    def test_user_form_same_persons(self):
        data = {'caption': 'caption-caption',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person_1': self.person_1_1.id,
                'person_2': self.person_1_1.id,
                'connection_type': persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertFalse(form.is_valid())

    def test_user_form__has_connection(self):
        persons_logic.create_social_connection(connection_type=persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER,
                                               person_1=self.person_1_1,
                                               person_2=self.person_2_1)
        data = {'caption': 'caption-caption',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person_1': self.person_1_1.id,
                'person_2': self.person_2_1.id,
                'connection_type': persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertFalse(form.is_valid())

    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_LIMIT', 1)
    def test_user_form__max_connections_first_master(self):
        persons_logic.create_social_connection(connection_type=persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER,
                                               person_1=self.person_1_1,
                                               person_2=self.person_2_2)
        data = {'caption': 'caption-caption',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person_1': self.person_1_1.id,
                'person_2': self.person_2_1.id,
                'connection_type': persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertFalse(form.is_valid())

    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_LIMIT', 1)
    def test_user_form__max_connections_second_master(self):
        persons_logic.create_social_connection(connection_type=persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER,
                                               person_1=self.person_2_1,
                                               person_2=self.person_2_2)
        data = {'caption': 'caption-caption',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person_1': self.person_1_1.id,
                'person_2': self.person_2_1.id,
                'connection_type': persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertFalse(form.is_valid())

    def test_user_form__not_in_inner_circle(self):
        data = {'caption': 'caption-caption',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person_1': self.person_2_1.id,
                'person_2': self.person_1_1.id,
                'connection_type': persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertFalse(form.is_valid())

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

        self.assertTrue(persons_storage.social_connections.get_connection_type(self.person_1_1, self.person_2_1))

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_has_meaning__already_connected(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        data = self.bill.user_form_initials
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form, self.account)
        self.assertTrue(self.bill.has_meaning())
        self.assertTrue(self.bill.apply())

        bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        bill.state = relations.BILL_STATE.VOTING
        bill.save()

        self.assertTrue(form.is_valid())
        bill.update_by_moderator(form, self.account1)

        self.assertFalse(bill.has_meaning())

    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_LIMIT', 1)
    def test_has_meanign__max_connections_first_master(self):
        persons_logic.create_social_connection(connection_type=persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER,
                                               person_1=self.person_1_1,
                                               person_2=self.person_2_2)

        self.assertFalse(self.bill.has_meaning())

    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_LIMIT', 1)
    def test_has_meanign__max_connections_second_master(self):
        persons_logic.create_social_connection(connection_type=persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER,
                                               person_1=self.person_2_1,
                                               person_2=self.person_2_2)

        self.assertFalse(self.bill.has_meaning())
