# coding: utf-8

import mock
import datetime

from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PlaceModifier

from the_tale.game.bills.tests.helpers import BaseTestPrototypes

from the_tale.game.map.places.modifiers import TradeCenter, CraftCenter


class PlaceModifierTests(BaseTestPrototypes):

    def setUp(self):
        super(PlaceModifierTests, self).setUp()

        self.place = self.place1
        self.place_2 = self.place2

        self.bill_data = PlaceModifier(place_id=self.place.id, modifier_id=TradeCenter.get_id(), modifier_name=TradeCenter.TYPE.text, old_modifier_name=None)

        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

    def test_create(self):
        self.assertEqual(self.bill.data.place_id, self.place.id)
        self.assertEqual(self.bill.data.modifier_id, TradeCenter.get_id())
        self.assertEqual(self.bill.data.modifier_name, TradeCenter.TYPE.text)
        self.assertEqual(self.bill.data.old_modifier_name, None)

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.place)])

    @mock.patch('the_tale.game.map.places.modifiers.prototypes.PlaceModifierBase.can_be_choosen', True)
    def test_update(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'place': self.place_2.id,
                                                         'chronicle_on_accepted': 'chronicle-on-accepted',
                                                         'new_modifier': CraftCenter.get_id()})
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.place_id, self.place_2.id)
        self.assertEqual(self.bill.data.modifier_id, CraftCenter.get_id())
        self.assertEqual(self.bill.data.modifier_name, CraftCenter.TYPE.text)
        self.assertEqual(self.bill.data.old_modifier_name, None)

    @mock.patch('the_tale.game.map.places.modifiers.prototypes.PlaceModifierBase.can_be_choosen', True)
    def test_success_form_validation(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-2',
                                                         'place': self.place_2.id,
                                                         'new_modifier': CraftCenter.get_id()})
        self.assertTrue(form.is_valid())

    @mock.patch('the_tale.game.map.places.modifiers.prototypes.PlaceModifierBase.can_be_choosen', False)
    def test_invalid_form_validation(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-2',
                                                         'place': self.place_2.id,
                                                         'new_modifier': CraftCenter.get_id()})
        self.assertFalse(form.is_valid())


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_apply(self):
        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        form = PlaceModifier.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertTrue(self.bill.apply())

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        self.assertNotEqual(self.place.modifier, None)
        self.assertEqual(self.place.modifier, TradeCenter(self.place) )
