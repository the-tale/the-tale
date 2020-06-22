
import smart_imports

smart_imports.all()


class BillDeclineResourceExchangeTests(helpers.BaseTestPrototypes):

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def setUp(self):
        super(BillDeclineResourceExchangeTests, self).setUp()

        self.resource_1, self.resource_2 = helpers.choose_exchange_resources()

        self.declined_bill_data = bills.place_resource_exchange.PlaceResourceExchange(place_1_id=self.place1.id,
                                                                                      place_2_id=self.place2.id,
                                                                                      resource_1=self.resource_1,
                                                                                      resource_2=self.resource_2)

        self.declined_bill = prototypes.BillPrototype.create(owner=self.account1,
                                                             caption='declined-bill-caption',
                                                             chronicle_on_accepted='chronicle-on-accepted',
                                                             bill=self.declined_bill_data)

        data = self.declined_bill.user_form_initials
        data['approved'] = True
        declined_form = self.declined_bill.data.get_moderator_form_update(data)

        self.assertTrue(declined_form.is_valid())
        self.declined_bill.update_by_moderator(declined_form, self.account1)
        self.declined_bill.apply()

        self.bill_data = bills.bill_decline.BillDecline(declined_bill_id=self.declined_bill.id)
        self.bill = prototypes.BillPrototype.create(self.account1, 'bill-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted',)

    def test_create(self):
        self.assertEqual(self.bill.data.declined_bill_id, self.declined_bill.id)
        self.assertEqual(self.bill.data.declined_bill.id, self.declined_bill.id)

    def test_user_form_initials(self):
        self.assertEqual(self.bill.data.user_form_initials(),
                         {'declined_bill': self.declined_bill.id})

    def test_actors(self):
        self.assertEqual(self.bill_data.actors, self.declined_bill.data.actors)

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_update(self):
        declined_bill_2 = prototypes.BillPrototype.create(self.account1, 'declined-bill-caption',
                                                          self.declined_bill_data, chronicle_on_accepted='chronicle-on-accepted-2')

        data = declined_bill_2.user_form_initials
        data['approved'] = True
        declined_form = declined_bill_2.data.get_moderator_form_update(data)

        self.assertTrue(declined_form.is_valid())
        declined_bill_2.update_by_moderator(declined_form, self.account1)
        declined_bill_2.apply()

        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-3',
                                                         'declined_bill': declined_bill_2.id})
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = prototypes.BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.declined_bill_id, declined_bill_2.id)

    def test_form_validation__success(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'some caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-3',
                                                         'declined_bill': self.declined_bill.id})
        self.assertTrue(form.is_valid())

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_user_form_validation__wrong_bill(self):
        bill_data = bills.place_description.PlaceDescripton(place_id=self.place1.id, description='new description')
        bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', bill_data, chronicle_on_accepted='chronicle-on-accepted',)

        data = bill.user_form_initials
        data['approved'] = True
        form = bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        bill.update_by_moderator(form, self.account1)
        self.assertTrue(bill.apply())

        form = self.bill.data.get_user_form_update(post={'caption': 'caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-3',
                                                         'declined_bill': bill.id})
        self.assertFalse(form.is_valid())

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_apply(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        old_storage_version = places_storage.resource_exchanges._version

        self.assertEqual(len(places_storage.resource_exchanges.all()), 1)

        data = self.bill.user_form_initials
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form, self.account1)

        self.assertTrue(self.bill.apply())

        self.assertNotEqual(old_storage_version, places_storage.resource_exchanges._version)
        self.assertEqual(len(places_storage.resource_exchanges.all()), 0)

        bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        declined_bill = prototypes.BillPrototype.get_by_id(self.declined_bill.id)
        self.assertTrue(declined_bill.state.is_ACCEPTED)
        self.assertTrue(declined_bill.is_declined)
        self.assertTrue(declined_bill.declined_by.id, bill.id)

    def test_has_meaning(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        data = self.bill.user_form_initials
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form, self.account1)

        self.assertTrue(self.bill.has_meaning())

        self.declined_bill.is_declined = True
        self.declined_bill.save()

        self.assertFalse(self.bill.has_meaning())

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_reapply(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        old_storage_version = places_storage.resource_exchanges._version

        self.assertEqual(len(places_storage.resource_exchanges.all()), 1)

        data = self.bill.user_form_initials
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form, self.account1)

        self.assertTrue(self.bill.apply())

        self.bill.state = relations.BILL_STATE.VOTING
        self.bill.save()

        with mock.patch('the_tale.game.bills.prototypes.BillPrototype.decline') as skipped_decline:
            self.assertTrue(self.bill.apply())

        self.assertEqual(skipped_decline.call_count, 0)

        self.assertNotEqual(old_storage_version, places_storage.resource_exchanges._version)
        self.assertEqual(len(places_storage.resource_exchanges.all()), 0)

        bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        declined_bill = prototypes.BillPrototype.get_by_id(self.declined_bill.id)
        self.assertTrue(declined_bill.state.is_ACCEPTED)
        self.assertTrue(declined_bill.is_declined)
        self.assertTrue(declined_bill.declined_by.id, bill.id)
