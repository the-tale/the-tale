
import smart_imports

smart_imports.all()


TEST_FREEDOM = float(666)


class PersonChronicleTests(helpers.BaseTestPrototypes):

    def setUp(self):
        super(PersonChronicleTests, self).setUp()

        self.person1 = sorted(self.place1.persons, key=lambda person: -politic_power_storage.persons.total_power_fraction(person.id))[0]
        self.person2 = sorted(self.place2.persons, key=lambda person: -politic_power_storage.persons.total_power_fraction(person.id))[-1]

        self.bill_data = bills.person_chronicle.PersonChronicle(person_id=self.person1.id,
                                                                old_place_name_forms=self.place1.utg_name,
                                                                power_bonus=relations.POWER_BONUS_CHANGES.UP)
        self.bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted')

    def test_create(self):
        self.assertEqual(self.bill.data.person_id, self.person1.id)
        self.assertTrue(self.bill.data.power_bonus.is_UP)

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.person1.place), id(self.person1)])

    def test_update(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-2',
                                                         'person': self.person2.id})
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = prototypes.BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.person_id, self.person2.id)
        self.assertTrue(self.bill.data.power_bonus.is_NOT_CHANGE)

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_apply(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        data = self.bill.user_form_initials
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertTrue(self.bill.apply())

        bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)
