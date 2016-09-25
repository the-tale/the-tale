# coding: utf-8

import mock
import datetime

from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PersonRemove

from the_tale.game.persons.models import Person

from the_tale.game.bills.tests.helpers import BaseTestPrototypes


class PersonRemoveTests(BaseTestPrototypes):

    def setUp(self):
        super(PersonRemoveTests, self).setUp()

        self.person1 = sorted(self.place1.persons, key=lambda p: -p.total_politic_power_fraction)[0]
        self.person2 = sorted(self.place2.persons, key=lambda p: -p.total_politic_power_fraction)[-1]

        self.bill_data = PersonRemove(person_id=self.person1.id, old_place_name_forms=self.place1.utg_name)
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')


    def test_create(self):
        self.assertEqual(self.bill.data.person_id, self.person1.id)

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.person1.place)])
