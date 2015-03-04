# coding: utf-8

import mock
import datetime

from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PersonChronicle

from the_tale.game.bills import relations

from the_tale.game.bills.tests.helpers import BaseTestPrototypes


class PersonChronicleTests(BaseTestPrototypes):

    def setUp(self):
        super(PersonChronicleTests, self).setUp()

        self.person1 = sorted(self.place1.persons, key=lambda p: -p.power)[0]
        self.person2 = sorted(self.place2.persons, key=lambda p: -p.power)[-1]

        self.bill_data = PersonChronicle(person_id=self.person1.id, old_place_name_forms=self.place1.utg_name, power_bonus=relations.POWER_BONUS_CHANGES.UP)
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')


    def test_create(self):
        self.assertEqual(self.bill.data.person_id, self.person1.id)
        self.assertTrue(self.bill.data.power_bonus.is_UP)

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.person1.place)])

    def test_update(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'rationale': 'new-rationale',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-2',
                                                         'person': self.person2.id,
                                                         'power_bonus': relations.POWER_BONUS_CHANGES.DOWN })
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.person_id, self.person2.id)
        self.assertTrue(self.bill.data.power_bonus.is_DOWN)


    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def check_apply(self, change_power_mock):
        VotePrototype.create(self.account2, self.bill, False)
        VotePrototype.create(self.account3, self.bill, True)

        form = PersonChronicle.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        with mock.patch('the_tale.game.persons.prototypes.PersonPrototype.cmd_change_power') as cmd_change_power:
            self.assertTrue(self.bill.apply())

        self.assertEqual(cmd_change_power.call_args_list, change_power_mock)

        bill = BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

    def test_apply_up(self):
        self.bill.data.power_bonus = relations.POWER_BONUS_CHANGES.UP
        self.check_apply([mock.call(power=0,
                                   positive_bonus=relations.POWER_BONUS_CHANGES.UP.bonus_delta,
                                   negative_bonus=0)])

    def test_apply_down(self):
        self.bill.data.power_bonus = relations.POWER_BONUS_CHANGES.DOWN
        self.check_apply([mock.call(power=0,
                                   positive_bonus=0,
                                   negative_bonus=relations.POWER_BONUS_CHANGES.UP.bonus_delta)])

    def test_apply_not_change(self):
        self.bill.data.power_bonus = relations.POWER_BONUS_CHANGES.NOT_CHANGE
        self.check_apply([])
