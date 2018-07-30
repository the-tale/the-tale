
import smart_imports

smart_imports.all()


class PersonRemoveTests(helpers.BaseTestPrototypes):

    def setUp(self):
        super(PersonRemoveTests, self).setUp()

        self.person1 = sorted(self.place1.persons, key=lambda person: -politic_power_storage.persons.total_power_fraction(person.id))[0]
        self.person2 = sorted(self.place2.persons, key=lambda person: -politic_power_storage.persons.total_power_fraction(person.id))[-1]

        self.bill_data = bills.person_remove.PersonRemove(person_id=self.person1.id, old_place_name_forms=self.place1.utg_name)
        self.bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

    def test_create(self):
        self.assertEqual(self.bill.data.person_id, self.person1.id)

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.person1.place)])
