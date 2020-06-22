
import smart_imports

smart_imports.all()


TEST_FREEDOM = float(666)


class EmissaryChronicleTests(clans_helpers.ClansTestsMixin,
                             emissaries_helpers.EmissariesTestsMixin,
                             helpers.BaseTestPrototypes):

    def setUp(self):
        super().setUp()

        self.prepair_forum_for_clans()

        self.clan = self.create_clan(owner=self.account1, uid=1)

        self.emissary_1 = self.create_emissary(clan=self.clan,
                                               initiator=self.account1,
                                               place_id=self.place1.id)

        self.emissary_2 = self.create_emissary(clan=self.clan,
                                               initiator=self.account1,
                                               place_id=self.place2.id)

        self.bill_data = bills.emissary_chronicle.EmissaryChronicle(emissary_id=self.emissary_1.id,
                                                                    old_place_name_forms=self.place1.utg_name)
        self.bill = prototypes.BillPrototype.create(self.account1,
                                                    'bill-1-caption',
                                                    self.bill_data,
                                                    chronicle_on_accepted='chronicle-on-accepted')

    def test_create(self):
        self.assertEqual(self.bill.data.emissary_id, self.emissary_1.id)

    def test_actors(self):
        self.assertEqual([id(a) for a in self.bill_data.actors], [id(self.emissary_1.place), id(self.emissary_1)])

    def test_update(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-2',
                                                         'emissary': self.emissary_2.id},
                                                   owner_id=self.account1.id)
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = prototypes.BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.emissary_id, self.emissary_2.id)

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_apply(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        data = self.bill.user_form_initials
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form, self.account1)

        self.assertTrue(self.bill.apply())

        bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)
