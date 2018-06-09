
from unittest import mock
import datetime

from the_tale.game import turn
from the_tale.game import tt_api_impacts

from the_tale.game.politic_power import logic as politic_power_logic

from the_tale.game.persons import storage as persons_storage
from the_tale.game.persons import logic as persons_logic

from the_tale.game.bills import relations
from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PersonMove
from the_tale.game.bills.tests.helpers import BaseTestPrototypes


class PersonMoveTests(BaseTestPrototypes):

    def setUp(self):
        super(PersonMoveTests, self).setUp()

        self.person_1, self.person_2, self.person_3 = self.place1.persons[0:3]

        self.account = self.accounts_factory.create_account()

        politic_power_logic.add_power_impacts(persons_logic.tt_power_impacts(person_inner_circle=True,
                                                                             place_inner_circle=True,
                                                                             actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                             actor_id=self.account.id,
                                                                             person=self.person_1,
                                                                             amount=100,
                                                                             fame=0))

        politic_power_logic.add_power_impacts(persons_logic.tt_power_impacts(person_inner_circle=True,
                                                                             place_inner_circle=True,
                                                                             actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                             actor_id=self.account.id,
                                                                             person=self.person_2,
                                                                             amount=100,
                                                                             fame=0))

        self.bill_data = PersonMove(person_id=self.person_1.id, new_place_id=self.place2.id)
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

    def test_create(self):
        self.assertEqual(self.bill.data.person_id, self.person_1.id)
        self.assertEqual(self.bill.data.place_id, self.place1.id)
        self.assertEqual(self.bill.data.new_place_id, self.place2.id)
        self.assertEqual(self.bill.data.new_place_name_forms, self.place2.utg_name)

    def test_actors(self):
        self.assertEqual(set([id(a) for a in self.bill_data.actors]),
                         set([id(self.place1), id(self.place2), id(self.person_1)]))

    @mock.patch('the_tale.game.balance.constants.PERSON_MOVE_DELAY', 0)
    def test_update(self):
        data = {'caption': 'new-caption',
                'chronicle_on_accepted': 'new-chronicle-on-accepted',
                'person': self.person_2.id,
                'new_place': self.place3.id}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        form.is_valid()

        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.person_id, self.person_2.id)
        self.assertEqual(self.bill.data.new_place_id, self.place3.id)
        self.assertEqual(self.bill.data.new_place_name_forms, self.place3.utg_name)

    @mock.patch('the_tale.game.balance.constants.PERSON_MOVE_DELAY', 1)
    def test_user_form__move_delay(self):
        data = {'caption': 'caption-caption',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person': self.person_2.id,
                'new_place': self.place3.id}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertFalse(form.is_valid())

        turn.increment()

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)

        self.assertTrue(form.is_valid())

    @mock.patch('the_tale.game.balance.constants.PERSON_MOVE_DELAY', 0)
    @mock.patch('the_tale.game.balance.constants.PLACE_MIN_PERSONS', 100)
    def test_user_form__min_barrier(self):
        data = {'caption': 'caption-caption',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person': self.person_2.id,
                'new_place': self.place3.id}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertFalse(form.is_valid())

    @mock.patch('the_tale.game.balance.constants.PERSON_MOVE_DELAY', 0)
    @mock.patch('the_tale.game.balance.constants.PLACE_MAX_PERSONS', 1)
    def test_user_form__max_barrier(self):
        data = {'caption': 'caption-caption',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person': self.person_2.id,
                'new_place': self.place3.id}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertFalse(form.is_valid())

    @mock.patch('the_tale.game.balance.constants.PERSON_MOVE_DELAY', 0)
    def test_user_form__not_in_inner_circle(self):
        data = {'caption': 'caption-caption',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person': self.person_3.id,
                'new_place': self.place3.id}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertFalse(form.is_valid())

    @mock.patch('the_tale.game.persons.objects.Person.has_building', True)
    def test_user_form__has_building(self):
        data = {'caption': 'caption-caption',
                'chronicle_on_accepted': 'chronicle-on-accepted',
                'person': self.person_2.id,
                'new_place': self.place3.id}

        form = self.bill.data.get_user_form_update(post=data, owner_id=self.account.id)
        self.assertFalse(form.is_valid())

    @mock.patch('the_tale.game.balance.constants.PERSON_MOVE_DELAY', 0)
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

        person = persons_storage.persons[self.person_1.id]

        self.assertEqual(person.place.id, self.place2.id)

    @mock.patch('the_tale.game.balance.constants.PERSON_MOVE_DELAY', 0)
    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_has_meaning__already_in_town(self):
        VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        data = self.bill.user_form_initials
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)
        self.assertTrue(self.bill.has_meaning())
        self.assertTrue(self.bill.apply())

        bill = BillPrototype.get_by_id(self.bill.id)
        bill.state = relations.BILL_STATE.VOTING
        bill.save()

        self.assertTrue(form.is_valid())
        bill.update_by_moderator(form)

        self.assertFalse(bill.has_meaning())

    @mock.patch('the_tale.game.balance.constants.PLACE_MIN_PERSONS', 100)
    def test_has_meaning__min_barrier(self):
        self.assertFalse(self.bill.has_meaning())

    @mock.patch('the_tale.game.balance.constants.PLACE_MAX_PERSONS', 1)
    def test_has_meaning__max_barrier(self):
        self.assertFalse(self.bill.has_meaning())

    @mock.patch('the_tale.game.balance.constants.PERSON_MOVE_DELAY', 1)
    def test_has_meaning__move_delay(self):
        self.assertFalse(self.bill.has_meaning())

        turn.increment()

        self.assertTrue(self.bill.has_meaning())

    @mock.patch('the_tale.game.persons.objects.Person.has_building', True)
    def test_has_meaning__has_building(self):
        self.assertFalse(self.bill.has_meaning())
