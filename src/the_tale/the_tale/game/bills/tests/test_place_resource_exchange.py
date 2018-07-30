
import smart_imports

smart_imports.all()


class PlaceResourceExchangeTests(helpers.BaseTestPrototypes):

    def setUp(self):
        super(PlaceResourceExchangeTests, self).setUp()

        self.resource_1, self.resource_2 = helpers.choose_exchange_resources()

        self.bill_data = bills.place_resource_exchange.PlaceResourceExchange(place_1_id=self.place1.id,
                                                                             place_2_id=self.place2.id,
                                                                             resource_1=self.resource_1,
                                                                             resource_2=self.resource_2)

        self.bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data,
                                                    chronicle_on_accepted='chronicle-on-accepted')

    def test_create(self):
        self.assertEqual(self.bill.data.place_1_id, self.place1.id)
        self.assertEqual(self.bill.data.place_2_id, self.place2.id)
        self.assertEqual(self.bill.data.resource_1, self.resource_1)
        self.assertEqual(self.bill.data.resource_2, self.resource_2)
        self.assertEqual(self.bill.data.old_place_1_name_forms, self.place1.utg_name)
        self.assertEqual(self.bill.data.old_place_2_name_forms, self.place2.utg_name)

        self.assertEqual(self.bill.data.place_1.id, self.place1.id)
        self.assertEqual(self.bill.data.place_2.id, self.place2.id)

        self.assertEqual(self.bill.data.old_place_1_name, self.place1.utg_name.normal_form())
        self.assertEqual(self.bill.data.old_place_2_name, self.place2.utg_name.normal_form())

        self.assertFalse(self.bill.data.place_1_name_changed)
        self.assertFalse(self.bill.data.place_2_name_changed)

    def test_user_form_initials(self):
        self.assertEqual(self.bill.data.user_form_initials(),
                         {'place_1': self.bill.data.place_1_id,
                          'place_2': self.bill.data.place_2_id,
                          'resource_1': self.bill.data.resource_1,
                          'resource_2': self.bill.data.resource_2})

    def test_actors(self):
        self.assertEqual(set(id(a) for a in self.bill_data.actors), set([id(self.place1), id(self.place2)]))

    def test_update(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'new-caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted-2',
                                                         'place_1': self.place2.id,
                                                         'place_2': self.place1.id,
                                                         'resource_1': self.resource_2,
                                                         'resource_2': self.resource_1})
        self.assertTrue(form.is_valid())

        self.bill.update(form)

        self.bill = prototypes.BillPrototype.get_by_id(self.bill.id)

        self.assertEqual(self.bill.data.place_1_id, self.place2.id)
        self.assertEqual(self.bill.data.place_2_id, self.place1.id)
        self.assertEqual(self.bill.data.resource_1, self.resource_2)
        self.assertEqual(self.bill.data.resource_2, self.resource_1)
        self.assertEqual(self.bill.data.old_place_1_name_forms, self.place2.utg_name)
        self.assertEqual(self.bill.data.old_place_2_name_forms, self.place1.utg_name)

        self.assertEqual(self.bill.data.place_1.id, self.place2.id)
        self.assertEqual(self.bill.data.place_2.id, self.place1.id)

        self.assertEqual(self.bill.data.old_place_1_name, self.place2.utg_name.normal_form())
        self.assertEqual(self.bill.data.old_place_2_name, self.place1.utg_name.normal_form())

        self.assertFalse(self.bill.data.place_2_name_changed)
        self.assertFalse(self.bill.data.place_1_name_changed)

    def test_form_validation__success(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'long caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted',
                                                         'place_1': self.place1.id,
                                                         'place_2': self.place2.id,
                                                         'resource_1': self.resource_1,
                                                         'resource_2': self.resource_2})
        self.assertTrue(form.is_valid())

    def test_user_form_validation__not_connected(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'long caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted',
                                                         'place_1': self.place1.id,
                                                         'place_2': self.place3.id,
                                                         'resource_1': self.resource_2,
                                                         'resource_2': self.resource_1})
        self.assertFalse(form.is_valid())

    @mock.patch('the_tale.game.balance.constants.PLACE_MAX_BILLS_NUMBER', 0)
    def test_user_form_validation__maximum_exchanges_reached(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'long caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted',
                                                         'place_1': self.place1.id,
                                                         'place_2': self.place2.id,
                                                         'resource_1': self.resource_1,
                                                         'resource_2': self.resource_2})
        self.assertFalse(form.is_valid())

    def test_user_form_validation__equal_parameters(self):
        form = self.bill.data.get_user_form_update(post={'caption': 'long caption',
                                                         'chronicle_on_accepted': 'chronicle-on-accepted',
                                                         'place_1': self.place1.id,
                                                         'place_2': self.place2.id,
                                                         'resource_1': self.resource_1,
                                                         'resource_2': self.resource_1})
        self.assertFalse(form.is_valid())

    def test_user_form_validation__not_allowed_resources(self):
        for resource in places_relations.RESOURCE_EXCHANGE_TYPE.records:
            if resource.is_NONE:
                continue

            form = self.bill.data.get_user_form_update(post={'caption': 'long caption',
                                                             'chronicle_on_accepted': 'chronicle-on-accepted',
                                                             'place_1': self.place1.id,
                                                             'place_2': self.place2.id,
                                                             'resource_1': resource,
                                                             'resource_2': places_relations.RESOURCE_EXCHANGE_TYPE.NONE})

            self.assertEqual(form.is_valid(), resource in bills.place_resource_exchange.ALLOWED_EXCHANGE_TYPES)

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def apply_bill(self):
        prototypes.VotePrototype.create(self.account2, self.bill, relations.VOTE_TYPE.AGAINST)
        prototypes.VotePrototype.create(self.account3, self.bill, relations.VOTE_TYPE.FOR)

        data = self.bill.user_form_initials
        data['approved'] = True
        form = self.bill.data.get_moderator_form_update(data)

        self.assertTrue(form.is_valid())
        self.bill.update_by_moderator(form)

        self.assertEqual(len(places_storage.resource_exchanges.all()), 0)

        self.assertTrue(self.bill.apply())

    def test_apply(self):

        old_storage_version = places_storage.resource_exchanges._version

        self.apply_bill()

        self.assertNotEqual(old_storage_version, places_storage.resource_exchanges._version)
        self.assertEqual(len(places_storage.resource_exchanges.all()), 1)

        bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(bill.state.is_ACCEPTED)

        exchange = places_storage.resource_exchanges.all()[0]

        self.assertEqual(set([exchange.place_1.id, exchange.place_2.id]), set([self.place1.id, self.place2.id]))
        self.assertEqual(set([exchange.resource_1, exchange.resource_2]), set([self.resource_1, self.resource_2]))
        self.assertEqual(exchange.bill_id, bill.id)

    def test_decline__success(self):
        self.apply_bill()

        old_storage_version = places_storage.resource_exchanges._version

        decliner = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted-2')

        self.bill.decline(decliner)

        self.assertNotEqual(old_storage_version, places_storage.resource_exchanges._version)

        self.assertEqual(len(places_storage.resource_exchanges.all()), 0)

    def test_decline__no_excange(self):
        self.apply_bill()

        places_prototypes.ResourceExchangePrototype._db_all().delete()

        places_storage.resource_exchanges.refresh()

        self.assertEqual(len(places_storage.resource_exchanges.all()), 0)

        old_storage_version = places_storage.resource_exchanges._version

        decliner = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', self.bill_data, chronicle_on_accepted='chronicle-on-accepted-2')

        self.bill.decline(decliner)

        self.assertEqual(old_storage_version, places_storage.resource_exchanges._version)

    def test_end__success(self):
        self.apply_bill()

        old_storage_version = places_storage.resource_exchanges._version

        self.bill.end()

        self.assertNotEqual(old_storage_version, places_storage.resource_exchanges._version)

        self.assertEqual(len(places_storage.resource_exchanges.all()), 0)

    def test_end__no_excange(self):
        self.apply_bill()

        places_prototypes.ResourceExchangePrototype._db_all().delete()

        places_storage.resource_exchanges.refresh()

        self.assertEqual(len(places_storage.resource_exchanges.all()), 0)

        old_storage_version = places_storage.resource_exchanges._version

        self.bill.end()

        self.assertEqual(old_storage_version, places_storage.resource_exchanges._version)

    def test_has_meaning__not_connected(self):
        bill_data = bills.place_resource_exchange.PlaceResourceExchange(place_1_id=self.place1.id,
                                                                        place_2_id=self.place3.id,
                                                                        resource_1=self.resource_1,
                                                                        resource_2=self.resource_2)

        bill = prototypes.BillPrototype.create(self.account1, 'bill-1-caption', bill_data,
                                               chronicle_on_accepted='chronicle-on-accepted')

        self.assertFalse(bill.has_meaning())

    @mock.patch('the_tale.game.balance.constants.PLACE_MAX_BILLS_NUMBER', 0)
    def test_has_meaning__maximum_exchanges_reached(self):
        self.assertFalse(self.bill.has_meaning())
