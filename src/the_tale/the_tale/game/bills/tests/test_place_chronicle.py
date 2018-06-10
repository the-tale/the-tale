
from unittest import mock
import datetime

from the_tale.game.politic_power import logic as politic_power_logic
from the_tale.game import tt_api_impacts

from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PlaceChronicle

from the_tale.game.bills import relations

from the_tale.game.bills.tests.helpers import BaseTestPrototypes


TEST_FREEDOM = float(666)


class PlaceChronicleTests(BaseTestPrototypes):

    def setUp(self):
        super(PlaceChronicleTests, self).setUp()

        self.bill_data = PlaceChronicle(place_id=self.place1.id, old_name_forms=self.place1.utg_name, power_bonus=relations.POWER_BONUS_CHANGES.UP)
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

    def test_create(self):
        self.assertEqual(self.bill.data.place_id, self.place1.id)
        self.assertTrue(self.bill.data.power_bonus.is_UP)

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.place1)])

    def test_update(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-2',
                                                         'place': self.place2.id,
                                                         'power_bonus': relations.POWER_BONUS_CHANGES.DOWN })
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.place_id, self.place2.id)
        self.assertTrue(self.bill.data.power_bonus.is_DOWN)

    @mock.patch('the_tale.game.places.attributes.Attributes.freedom', TEST_FREEDOM)
    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def check_apply(self):
        tt_api_impacts.debug_clear_service()

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

        impacts = politic_power_logic.get_last_power_impacts(limit=100)

        return impacts

    def test_apply_up(self):
        self.bill.data.power_bonus = relations.POWER_BONUS_CHANGES.UP

        impacts = self.check_apply()

        self.assertEqual(len(impacts), 1)

        self.assertEqual(impacts[0].amount, relations.POWER_BONUS_CHANGES.UP.bonus * TEST_FREEDOM)
        self.assertTrue(impacts[0].type.is_OUTER_CIRCLE)
        self.assertTrue(impacts[0].target_type.is_PLACE)
        self.assertEqual(impacts[0].target_id, self.place1.id)
        self.assertTrue(impacts[0].actor_type.is_BILL)
        self.assertEqual(impacts[0].actor_id, self.bill.id)

    def test_apply_down(self):
        self.bill.data.power_bonus = relations.POWER_BONUS_CHANGES.DOWN

        impacts = self.check_apply()

        self.assertEqual(len(impacts), 1)

        self.assertEqual(impacts[0].amount, relations.POWER_BONUS_CHANGES.DOWN.bonus * TEST_FREEDOM)
        self.assertTrue(impacts[0].type.is_OUTER_CIRCLE)
        self.assertTrue(impacts[0].target_type.is_PLACE)
        self.assertEqual(impacts[0].target_id, self.place1.id)
        self.assertTrue(impacts[0].actor_type.is_BILL)
        self.assertEqual(impacts[0].actor_id, self.bill.id)

    def test_apply_not_change(self):
        self.bill.data.power_bonus = relations.POWER_BONUS_CHANGES.NOT_CHANGE

        impacts = self.check_apply()

        self.assertEqual(len(impacts), 0)
