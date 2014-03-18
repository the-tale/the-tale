# coding: utf-8

import mock
import datetime

from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PlaceDescripton

from the_tale.game.bills.tests.helpers import BaseTestPrototypes

from the_tale.game.map.places.storage import places_storage
from the_tale.game.map.places.conf import places_settings


class PlaceDescriptionTests(BaseTestPrototypes):

    def setUp(self):
        super(PlaceDescriptionTests, self).setUp()

        self.place = places_storage.all()[0]
        self.place.description = 'old description'
        self.place.save()

        self.place_2 = places_storage.all()[1]

        self.bill_data = PlaceDescripton(place_id=self.place.id, description='new description')
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data)

    def test_create(self):
        self.assertEqual(self.bill.data.place_id, self.place.id)
        self.assertEqual(self.bill.data.description, 'new description')

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.place)])

    def test_update(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'place': self.place_2.id,
                                                         'new_description': 'new new description'})
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.place_id, self.place_2.id)
        self.assertEqual(self.bill.data.description, 'new new description')

    def test_long_description_error(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'place': self.place_2.id,
                                                         'new_description': '!' * (places_settings.MAX_DESCRIPTION_LENGTH+1)})
        self.assertFalse(form.is_valid())


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_apply(self):
        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        form = PlaceDescripton.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertTrue(self.bill.apply())

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        self.assertNotEqual(self.place.description, 'old description' )
        self.assertEqual(self.place.description, 'new description' )
