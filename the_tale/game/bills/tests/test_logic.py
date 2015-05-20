# coding: utf-8
import time
import datetime

import mock

from the_tale.forum.models import Post

from the_tale.accounts import prototypes as accounts_prototypes
from the_tale.accounts.achievements.relations import ACHIEVEMENT_TYPE

from the_tale.linguistics.tests import helpers as linguistics_helpers

from the_tale.game import names

from the_tale.game.prototypes import TimePrototype
from the_tale.game.balance import constants as c

from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.game.bills.models import Actor
from the_tale.game.bills import relations
from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PlaceRenaming, PlaceDescripton
from the_tale.game.bills.conf import bills_settings
from the_tale.game.bills import exceptions
from the_tale.game.bills import logic
from the_tale.game.bills.tests.helpers import BaseTestPrototypes

from the_tale.game.map.places.storage import places_storage


class LogicTests(BaseTestPrototypes):

    def setUp(self):
        super(LogicTests, self).setUp()


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_actual_bills_accepted_timestamps(self):
        from the_tale.game.bills import prototypes as bills_prototypes
        from the_tale.game.bills import bills
        from the_tale.game.bills import conf as bills_conf
        from the_tale.game.map.places import modifiers as places_modifiers
        from the_tale.forum import models as forum_models

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [])

        bill_data = bills.PlaceModifier(place_id=self.place1.id,
                                        modifier_id=places_modifiers.TradeCenter.get_id(),
                                        modifier_name=places_modifiers.TradeCenter.TYPE.text,
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
                                        modifier_id=places_modifiers.TradeCenter.get_id(),
                                        modifier_name=places_modifiers.TradeCenter.TYPE.text,
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
                                        modifier_id=places_modifiers.TradeCenter.get_id(),
                                        modifier_name=places_modifiers.TradeCenter.TYPE.text,
                                        old_modifier_name=None)
        bill_3 = bills_prototypes.BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id), [time.mktime(bill.voting_end_at.timetuple())])

        form = bills.PlaceModifier.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        bill_3.update_by_moderator(form)

        bill_3.apply()

        self.assertEqual(logic.actual_bills_accepted_timestamps(self.account1.id),
                         [time.mktime(bill.voting_end_at.timetuple()), time.mktime(bill_3.voting_end_at.timetuple())])
