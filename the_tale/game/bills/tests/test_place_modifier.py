# coding: utf-8

import mock
import datetime

from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PlaceModifier

from the_tale.game.bills.tests.helpers import BaseTestPrototypes

from the_tale.game.places import modifiers as places_modifiers
from the_tale.game.places import logic as places_logic


class PlaceModifierTests(BaseTestPrototypes):

    def setUp(self):
        super(PlaceModifierTests, self).setUp()

        self.place = self.place1
        self.place_2 = self.place2

        self.bill_data = PlaceModifier(place_id=self.place.id,
                                       modifier_id=places_modifiers.CITY_MODIFIERS.TRADE_CENTER,
                                       modifier_name=places_modifiers.CITY_MODIFIERS.TRADE_CENTER.text,
                                       old_modifier_name=None)

        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

    def test_create(self):
        self.assertEqual(self.bill.data.place_id, self.place.id)
        self.assertTrue(self.bill.data.modifier_id.is_TRADE_CENTER)
        self.assertEqual(self.bill.data.modifier_name, places_modifiers.CITY_MODIFIERS.TRADE_CENTER.text)
        self.assertEqual(self.bill.data.old_modifier_name, None)

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.place)])

    # @mock.patch('the_tale.game.places.modifiers.prototypes.PlaceModifierBase.can_be_choosen', True)
    def test_update(self):
        self.place_2.attrs.modifier_craft_center = 100
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'place': self.place_2.id,
                                                         'chronicle_on_accepted': 'chronicle-on-accepted',
                                                         'new_modifier': places_modifiers.CITY_MODIFIERS.CRAFT_CENTER})
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.place_id, self.place_2.id)
        self.assertTrue(self.bill.data.modifier_id.is_CRAFT_CENTER)
        self.assertEqual(self.bill.data.modifier_name, places_modifiers.CITY_MODIFIERS.CRAFT_CENTER.text)
        self.assertEqual(self.bill.data.old_modifier_name, None)

    def test_success_form_validation(self):
        self.place_2.attrs.modifier_craft_center = 100
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-2',
                                                         'place': self.place_2.id,
                                                         'new_modifier': places_modifiers.CITY_MODIFIERS.CRAFT_CENTER})
        self.assertTrue(form.is_valid())


    def test_not_allowed_modifier(self):
        self.place_2.attrs.modifier_craft_center = 0
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-2',
                                                         'place': self.place_2.id,
                                                         'new_modifier': places_modifiers.CITY_MODIFIERS.CRAFT_CENTER})
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

        self.assertTrue(self.place._modifier.is_TRADE_CENTER)


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_has_meaning__duplicate_modifier(self):
        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        form = PlaceModifier.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.bill.data.place.set_modifier(self.bill.data.modifier_id)

        places_logic.save_place(self.bill.data.place)

        self.assertFalse(self.bill.has_meaning())
