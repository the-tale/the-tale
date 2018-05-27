

from the_tale.game.politic_power import storage as politic_power_storage

from the_tale.game.bills.prototypes import BillPrototype
from the_tale.game.bills.bills import PersonRemove

from the_tale.game.bills.tests.helpers import BaseTestPrototypes


class PersonRemoveTests(BaseTestPrototypes):

    def setUp(self):
        super(PersonRemoveTests, self).setUp()

        self.person1 = sorted(self.place1.persons, key=lambda person: -politic_power_storage.persons.total_power_fraction(person.id))[0]
        self.person2 = sorted(self.place2.persons, key=lambda person: -politic_power_storage.persons.total_power_fraction(person.id))[-1]

        self.bill_data = PersonRemove(person_id=self.person1.id, old_place_name_forms=self.place1.utg_name)
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

    def test_create(self):
        self.assertEqual(self.bill.data.person_id, self.person1.id)

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.person1.place)])
