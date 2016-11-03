# coding: utf-8

from unittest import mock
import datetime

from the_tale.game.persons import logic as persons_logic
from the_tale.game.persons import storage as persons_storage
from the_tale.game.persons import relations as persons_relations

from the_tale.game.bills import relations
from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PersonRemoveSocialConnection
from the_tale.game.bills.tests.helpers import BaseTestPrototypes


class PersonRemoveSocialConnectionTests(BaseTestPrototypes):

    def setUp(self):
        super(PersonRemoveSocialConnectionTests, self).setUp()

        self.person_1_1 = self.place1.persons[0]
        self.person_2_1, self.person_2_2 = self.place2.persons[0:2]
        self.person_3_1 = self.place3.persons[0]

        self.account = self.accounts_factory.create_account()

        persons_logic.create_social_connection(connection_type=persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER,
                                               person_1=self.person_1_1,
                                               person_2=self.person_2_1)

        self.bill_data = PersonRemoveSocialConnection(person_1_id=self.person_1_1.id,
                                                      person_2_id=self.person_2_1.id)
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.person_1_1.politic_power.change_power(self.person_1_1, hero_id=self.account.id, has_in_preferences=True, power=100)


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
        self.person_2_2.politic_power.change_power(self.person_2_2, hero_id=self.account.id, has_in_preferences=True, power=100)

        persons_logic.create_social_connection(connection_type=persons_relations.SOCIAL_CONNECTION_TYPE.PARTNER,
                                               person_1=self.person_2_2,
                                               person_2=self.person_3_1)

        data = {'caption': 'new-caption',
                'rationale': 'new-rationale',
                'chronicle_on_accepted': 'new-chronicle-on-accepted',
                'person_1': self.person_2_2.id,
                'person_2': self.person_3_1.id}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)

        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.person_1_id, self.person_2_2.id)
        self.assertEqual(self.bill.data.person_2_id, self.person_3_1.id)
        self.assertEqual(self.bill.data.place_1_id, self.place2.id)
        self.assertEqual(self.bill.data.place_2_id, self.place3.id)
        self.assertEqual(self.bill.data.old_place_1_name, self.place2.utg_name)
        self.assertEqual(self.bill.data.old_place_2_name, self.place3.utg_name)


    def test_user_form__min_live_time(self):
        data = {'caption': 'caption-caption',
                'rationale': 'rationale',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person_1': self.person_1_1.id,
                'person_2': self.person_2_1.id}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertFalse(form.is_valid())


    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_MIN_LIVE_TIME', 0)
    def test_user_form__has_no_connection(self):
        data = {'caption': 'caption-caption',
                'rationale': 'rationale',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person_1': self.person_1_1.id,
                'person_2': self.person_2_2.id}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertFalse(form.is_valid())

    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_MIN_LIVE_TIME', 0)
    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_LIMIT', 1)
    def test_user_form__not_in_circles(self):
        data = {'caption': 'caption-caption',
                'rationale': 'rationale',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person_1': self.person_2_2.id,
                'person_2': self.person_3_1.id}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertFalse(form.is_valid())

    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_MIN_LIVE_TIME', 0)
    def test_user_form__second_in_circle(self):
        data = {'caption': 'caption-caption',
                'rationale': 'rationale',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person_1': self.person_2_1.id,
                'person_2': self.person_1_1.id}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertTrue(form.is_valid())


    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_MIN_LIVE_TIME', 0)
    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_apply(self):
        VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        data = self.bill.user_form_initials
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertTrue(self.bill.apply())

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        self.assertFalse(persons_storage.social_connections.is_connected(self.person_1_1, self.person_2_1))


    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_MIN_LIVE_TIME', 0)
    @mock.patch('the_tale.game.balance.constants.PERSON_SOCIAL_CONNECTIONS_LIMIT', 1)
    def test_has_meaning__no_connections(self):
        self.assertTrue(self.bill.has_meaning())
        connection = persons_storage.social_connections.get_connection(self.person_1_1, self.person_2_1)
        persons_logic.remove_connection(connection)
        self.assertFalse(self.bill.has_meaning())
