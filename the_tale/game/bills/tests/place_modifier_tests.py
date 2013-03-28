# coding: utf-8

import mock
import datetime

from game.bills.prototypes import BillPrototype, VotePrototype
from game.bills.bills import PlaceModifier

from game.bills.tests.prototype_tests import BaseTestPrototypes

from game.map.places.storage import places_storage
from game.map.places.modifiers import TradeCenter, CraftCenter


class PlaceModifierTests(BaseTestPrototypes):

    def setUp(self):
        super(PlaceModifierTests, self).setUp()

        self.place = places_storage.all()[0]
        self.place_2 = places_storage.all()[1]

        self.bill_data = PlaceModifier(place_id=self.place.id, modifier_id=TradeCenter.get_id(), modifier_name=TradeCenter.NAME, old_modifier_name=None)

        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data)

    def test_create(self):
        self.assertEqual(self.bill.data.place_id, self.place.id)
        self.assertEqual(self.bill.data.modifier_id, TradeCenter.get_id())
        self.assertEqual(self.bill.data.modifier_name, TradeCenter.NAME)
        self.assertEqual(self.bill.data.old_modifier_name, None)

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.place)])

    @mock.patch('game.map.places.modifiers.prototypes.PlaceModifierBase.can_be_choosen', True)
    def test_update(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'place': self.place_2.id,
                                                         'new_modifier': CraftCenter.get_id()})
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.place_id, self.place_2.id)
        self.assertEqual(self.bill.data.modifier_id, CraftCenter.get_id())
        self.assertEqual(self.bill.data.modifier_name, CraftCenter.NAME)
        self.assertEqual(self.bill.data.old_modifier_name, None)

    @mock.patch('game.map.places.modifiers.prototypes.PlaceModifierBase.can_be_choosen', True)
    def test_success_form_validation(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'place': self.place_2.id,
                                                         'new_modifier': CraftCenter.get_id()})
        self.assertTrue(form.is_valid())

    @mock.patch('game.map.places.modifiers.prototypes.PlaceModifierBase.can_be_choosen', False)
    def test_invalid_form_validation(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'place': self.place_2.id,
                                                         'new_modifier': CraftCenter.get_id()})
        self.assertFalse(form.is_valid())


    @mock.patch('game.bills.conf.bills_settings.MIN_VOTES_NUMBER', 2)
    @mock.patch('game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('game.bills.prototypes.BillPrototype.time_before_end_step', datetime.timedelta(seconds=0))
    def test_apply(self):
        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        form = PlaceModifier.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertTrue(self.bill.apply())

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state._is_ACCEPTED)

        self.assertNotEqual(self.place.modifier, None)
        self.assertEqual(self.place.modifier, TradeCenter(self.place) )
