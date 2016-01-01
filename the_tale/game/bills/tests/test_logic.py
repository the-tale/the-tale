# coding: utf-8
import time
import datetime

import mock

from .. import logic
from .helpers import BaseTestPrototypes


class LogicTests(BaseTestPrototypes):

    def setUp(self):
        super(LogicTests, self).setUp()


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_actual_bills_accepted_timestamps(self):
        from the_tale.game.bills import prototypes as bills_prototypes
        from the_tale.game.bills import bills
        from the_tale.game.places import modifiers as places_modifiers

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [])

        bill_data = bills.PlaceModifier(place_id=self.place1.id,
                                        modifier_id=places_modifiers.CITY_MODIFIERS.TRADE_CENTER,
                                        modifier_name=places_modifiers.CITY_MODIFIERS.TRADE_CENTER.text,
                                        old_modifier_name=None)
        bill = bills_prototypes.BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [])

        form = bills.PlaceModifier.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        bill.update_by_moderator(form)

        bill.apply()

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [time.mktime(bill.voting_end_at.timetuple())])

        # second bill

        bill_data = bills.PlaceModifier(place_id=self.place1.id,
                                        modifier_id=places_modifiers.CITY_MODIFIERS.TRADE_CENTER,
                                        modifier_name=places_modifiers.CITY_MODIFIERS.TRADE_CENTER.text,
                                        old_modifier_name=None)
        bill_2 = bills_prototypes.BillPrototype.create(self.account2, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [time.mktime(bill.voting_end_at.timetuple())])

        form = bills.PlaceModifier.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        bill_2.update_by_moderator(form)

        bill_2.apply()

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [time.mktime(bill.voting_end_at.timetuple())])

        # third bill

        bill_data = bills.PlaceModifier(place_id=self.place1.id,
                                        modifier_id=places_modifiers.CITY_MODIFIERS.TRADE_CENTER,
                                        modifier_name=places_modifiers.CITY_MODIFIERS.TRADE_CENTER.text,
                                        old_modifier_name=None)
        bill_3 = bills_prototypes.BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [time.mktime(bill.voting_end_at.timetuple())])

        form = bills.PlaceModifier.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        bill_3.update_by_moderator(form)

        bill_3.apply()

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id),
                         [time.mktime(bill.voting_end_at.timetuple()), time.mktime(bill_3.voting_end_at.timetuple())])
