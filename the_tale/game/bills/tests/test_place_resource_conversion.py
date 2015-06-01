# coding: utf-8

import mock
import datetime

from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PlaceResourceConversion


from the_tale.game.bills.tests.helpers import choose_conversions, BaseTestPrototypes

from the_tale.game.map.places.storage import resource_exchange_storage
from the_tale.game.map.places.prototypes import ResourceExchangePrototype


class PlaceResourceConversionTests(BaseTestPrototypes):

    def setUp(self):
        super(PlaceResourceConversionTests, self).setUp()

        self.conversion_1, self.conversion_2 = choose_conversions()

        self.bill_data = PlaceResourceConversion(place_id=self.place1.id,
                                                 conversion=self.conversion_1)

        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data,
                                         chronicle_on_accepted='chronicle-on-accepted')


    def test_create(self):
        self.assertEqual(self.bill.data.place_id, self.place1.id)
        self.assertEqual(self.bill.data.conversion, self.conversion_1)
        self.assertEqual(self.bill.data.old_place_name_forms, self.place1.utg_name)

        self.assertEqual(self.bill.data.place.id, self.place1.id)

        self.assertEqual(self.bill.data.old_place_name, self.place1.utg_name.normal_form())

        self.assertFalse(self.bill.data.place_name_changed)

    def test_user_form_initials(self):
        self.assertEqual(self.bill.data.user_form_initials,
                         {'place': self.bill.data.place_id,
                          'conversion': self.bill.data.conversion})

    def test_actors(self):
        self.assertEqual(set(id(a) for a in self.bill_data.actors), set([id(self.place1)]))

    def test_update(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted',
                                                         'place': self.place2.id,
                                                         'conversion': self.conversion_2})
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.place_id, self.place2.id)
        self.assertEqual(self.bill.data.conversion, self.conversion_2)
        self.assertEqual(self.bill.data.old_place_name_forms, self.place2.utg_name)

        self.assertEqual(self.bill.data.place.id, self.place2.id)

        self.assertEqual(self.bill.data.old_place_name, self.place2.utg_name.normal_form())

        self.assertFalse(self.bill.data.place_name_changed)


    def test_form_validation__success(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'long caption',
                                                         'rationale': 'long rationale',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted',
                                                         'place': self.place1.id,
                                                         'conversion': self.conversion_1})
        self.assertTrue(form.is_valid())

    @mock.patch('the_tale.game.balance.constants.PLACE_MAX_BILLS_NUMBER', 0)
    def test_user_form_validation__maximum_bills_reached(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'long caption',
                                                         'rationale': 'rationale',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted',
                                                         'place': self.place1.id,
                                                         'conversion': self.conversion_1})
        self.assertFalse(form.is_valid())


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def apply_bill(self):
        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        form = PlaceResourceConversion.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertEqual(len(resource_exchange_storage.all()), 0)

        self.assertTrue(self.bill.apply())

    def test_apply(self):

        old_storage_version = resource_exchange_storage._version

        self.apply_bill()

        self.assertNotEqual(old_storage_version, resource_exchange_storage._version)
        self.assertEqual(len(resource_exchange_storage.all()), 1)

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        exchange = resource_exchange_storage.all()[0]

        self.assertEqual(exchange.place_1.id, self.place1.id)
        self.assertEqual(exchange.place_2, None)
        self.assertEqual(exchange.resource_1, self.conversion_1.resource_from)
        self.assertEqual(exchange.resource_2, self.conversion_1.resource_to)
        self.assertEqual(exchange.bill_id, bill.id)

    def test_decline__success(self):
        self.apply_bill()

        old_storage_version = resource_exchange_storage._version

        decliner = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.bill.decline(decliner)

        self.assertNotEqual(old_storage_version, resource_exchange_storage._version)

        self.assertEqual(len(resource_exchange_storage.all()), 0)


    def test_decline__no_excange(self):
        self.apply_bill()

        ResourceExchangePrototype._db_all().delete()

        resource_exchange_storage.refresh()

        self.assertEqual(len(resource_exchange_storage.all()), 0)

        old_storage_version = resource_exchange_storage._version

        decliner = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.bill.decline(decliner)

        self.assertEqual(old_storage_version, resource_exchange_storage._version)


    def test_end__success(self):
        self.apply_bill()

        old_storage_version = resource_exchange_storage._version

        self.bill.end()

        self.assertNotEqual(old_storage_version, resource_exchange_storage._version)

        self.assertEqual(len(resource_exchange_storage.all()), 0)

    def test_end__no_excange(self):
        self.apply_bill()

        ResourceExchangePrototype._db_all().delete()

        resource_exchange_storage.refresh()

        self.assertEqual(len(resource_exchange_storage.all()), 0)

        old_storage_version = resource_exchange_storage._version

        self.bill.end()

        self.assertEqual(old_storage_version, resource_exchange_storage._version)
