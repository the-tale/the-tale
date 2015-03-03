# coding: utf-8

import mock
import datetime

from the_tale.game.map.places.storage import resource_exchange_storage

from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PlaceResourceExchange, BillDecline, PlaceDescripton
from the_tale.game.bills.tests.helpers import choose_exchange_resources, BaseTestPrototypes
from the_tale.game.bills.relations import BILL_STATE


class BillDeclineResourceExchangeTests(BaseTestPrototypes):

    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def setUp(self):
        super(BillDeclineResourceExchangeTests, self).setUp()

        self.resource_1, self.resource_2 = choose_exchange_resources()

        self.declined_bill_data = PlaceResourceExchange(place_1_id=self.place1.id,
                                                        place_2_id=self.place2.id,
                                                        resource_1=self.resource_1,
                                                        resource_2=self.resource_2)

        self.declined_bill = BillPrototype.create(owner=self.account1,
                                                  caption='declined-bill-caption',
                                                  rationale='declined-bill-rationale',
                                                  chronicle_on_accepted='chronicle-on-accepted',
                                                  bill=self.declined_bill_data)

        declined_form = PlaceResourceExchange.ModeratorForm({'approved': True})
        self.assertTrue(declined_form.is_valid())
        self.declined_bill.update_by_moderator(declined_form)
        self.declined_bill.apply()

        self.bill_data = BillDecline(declined_bill_id=self.declined_bill.id)
        self.bill = BillPrototype.create(self.account1, 'bill-caption', 'bill-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted',)

    def test_create(self):
        self.assertEqual(self.bill.data.declined_bill_id, self.declined_bill.id)
        self.assertEqual(self.bill.data.declined_bill.id, self.declined_bill.id)

    def test_user_form_initials(self):
        self.assertEqual(self.bill.data.user_form_initials,
                         {'bill': self.declined_bill.id})

    def test_actors(self):
        self.assertEqual(self.bill_data.actors, self.declined_bill.data.actors)

    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_update(self):
        declined_bill_2 = BillPrototype.create(self.account1, 'declined-bill-caption', 'declined-bill-rationale',
                                               self.declined_bill_data, chronicle_on_accepted='chronicle-on-accepted-2')
        declined_form = PlaceResourceExchange.ModeratorForm({'approved': True})
        self.assertTrue(declined_form.is_valid())
        declined_bill_2.update_by_moderator(declined_form)
        declined_bill_2.apply()

        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-3',
                                                         'declined_bill': declined_bill_2.id})
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.declined_bill_id, declined_bill_2.id)

    def test_form_validation__success(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'some caption',
                                                         'rationale': 'some rationale',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-3',
                                                         'declined_bill': self.declined_bill.id})
        self.assertTrue(form.is_valid())


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_user_form_validation__wrong_bill(self):
        bill_data = PlaceDescripton(place_id=self.place1.id, description='new description')
        bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted',)

        form = PlaceDescripton.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        bill.update_by_moderator(form)
        self.assertTrue(bill.apply())

        form = self.bill.data.get_user_form_update(post={'caption': 'caption',
                                                         'rationale': 'rationale',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-3',
                                                         'declined_bill': bill.id})
        self.assertFalse(form.is_valid())


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_apply(self):
        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        old_storage_version = resource_exchange_storage._version

        self.assertEqual(len(resource_exchange_storage.all()), 1)

        form = BillDecline.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertTrue(self.bill.apply())

        self.assertNotEqual(old_storage_version, resource_exchange_storage._version)
        self.assertEqual(len(resource_exchange_storage.all()), 0)

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        declined_bill = BillPrototype.get_by_id(self.declined_bill.id)
        self.assertTrue(declined_bill.state.is_ACCEPTED)
        self.assertTrue(declined_bill.is_declined)
        self.assertTrue(declined_bill.declined_by.id, bill.id)


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_reapply(self):
        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        old_storage_version = resource_exchange_storage._version

        self.assertEqual(len(resource_exchange_storage.all()), 1)

        form = BillDecline.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertTrue(self.bill.apply())

        self.bill.state = BILL_STATE.VOTING
        self.bill.save()

        with mock.patch('the_tale.game.bills.prototypes.BillPrototype.decline') as skipped_decline:
            self.assertTrue(self.bill.apply())

        self.assertEqual(skipped_decline.call_count, 0)

        self.assertNotEqual(old_storage_version, resource_exchange_storage._version)
        self.assertEqual(len(resource_exchange_storage.all()), 0)

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        declined_bill = BillPrototype.get_by_id(self.declined_bill.id)
        self.assertTrue(declined_bill.state.is_ACCEPTED)
        self.assertTrue(declined_bill.is_declined)
        self.assertTrue(declined_bill.declined_by.id, bill.id)
