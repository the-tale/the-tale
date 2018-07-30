
import smart_imports

smart_imports.all()


class RecordTests(utils_testcase.TestCase):

    def setUp(self):
        super(RecordTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        forum_category = forum_models.Category.objects.create(caption='category-1', slug='category-1')
        forum_models.SubCategory.objects.create(caption=bills_conf.settings.FORUM_CATEGORY_UID + '-caption',
                                                uid=bills_conf.settings.FORUM_CATEGORY_UID,
                                                category=forum_category)

        bill_data = bills_bills.place_renaming.PlaceRenaming(place_id=self.place_1.id, name_forms=game_names.generator().get_test_name('new_name'))
        self.bill = bills_prototypes.BillPrototype.create(self.account, 'bill-caption', bill_data, chronicle_on_accepted='chronicle-on-accepted')

    def test_records_for_every_type(self):
        types = set([record for record in relations.RECORD_TYPE.records if not record.deprecated])

        for record_class in list(records.RECORDS.values()):
            if record_class.TYPE in types:
                types.remove(record_class.TYPE)

        self.assertEqual(types, set())

    def create_test_word(self, index):
        return game_names.generator().get_test_name('new name %d' % index)

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def create_bill_decline__exchange(self):
        resource_1, resource_2 = bills_helpers.choose_exchange_resources()

        declined_bill_data = bills_bills.place_resource_exchange.PlaceResourceExchange(place_1_id=self.place_1.id,
                                                                                       place_2_id=self.place_2.id,
                                                                                       resource_1=resource_1,
                                                                                       resource_2=resource_2)

        declined_bill = bills_prototypes.BillPrototype.create(self.account, 'declined-bill-caption', declined_bill_data, chronicle_on_accepted='chronicle-on-accepted')

        declined_data = declined_bill.user_form_initials
        declined_data['approved'] = True

        declined_form = bills_bills.place_resource_exchange.PlaceResourceExchange.ModeratorForm(declined_data)
        self.assertTrue(declined_form.is_valid())
        declined_bill.update_by_moderator(declined_form)
        declined_bill.apply()

        bill_data = bills_bills.bill_decline.BillDecline(declined_bill_id=declined_bill.id)
        bill = bills_prototypes.BillPrototype.create(self.account, 'bill-caption', bill_data, chronicle_on_accepted='chronicle-on-accepted')
        return bill, declined_bill

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def create_bill_decline__conversion(self):
        conversion_1, conversion_2 = bills_helpers.choose_conversions()

        declined_bill_data = bills_bills.place_resource_conversion.PlaceResourceConversion(place_id=self.place_1.id,
                                                                                           conversion=conversion_1)

        declined_bill = bills_prototypes.BillPrototype.create(self.account, 'declined-bill-caption', declined_bill_data, chronicle_on_accepted='chronicle-on-accepted')

        declined_data = declined_bill.user_form_initials
        declined_data['approved'] = True

        declined_form = bills_bills.place_resource_conversion.PlaceResourceConversion.ModeratorForm(declined_data)
        self.assertTrue(declined_form.is_valid())
        declined_bill.update_by_moderator(declined_form)
        declined_bill.apply()

        bill_data = bills_bills.bill_decline.BillDecline(declined_bill_id=declined_bill.id)
        bill = bills_prototypes.BillPrototype.create(self.account, 'bill-caption', bill_data, chronicle_on_accepted='chronicle-on-accepted')
        return bill, declined_bill

    def test_bill_decline__actors__exchange(self):
        from the_tale.game.chronicle.signal_processors import _get_bill_decline_bill_arguments

        bill, declined_bill = self.create_bill_decline__exchange()

        actors_ids = []
        for role, actor in _get_bill_decline_bill_arguments(bill)['actors']:
            actors_ids.append((role, actor.id))
        self.assertEqual(set(actors_ids), set([(relations.ACTOR_ROLE.BILL, bill.id),
                                               (relations.ACTOR_ROLE.BILL, declined_bill.id),
                                               (relations.ACTOR_ROLE.PLACE, self.place_1.id),
                                               (relations.ACTOR_ROLE.PLACE, self.place_2.id)]))

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_bill_decline__actors_on_creation_record__exchange(self):
        bill, declined_bill = self.create_bill_decline__exchange()

        data = bill.user_form_initials
        data['approved'] = True

        form = bills_bills.bill_decline.BillDecline.ModeratorForm(data)
        self.assertTrue(form.is_valid())

        bill.update_by_moderator(form)

        self.assertTrue(bill.apply())

    def test_bill_decline__actors__convesion(self):
        from the_tale.game.chronicle.signal_processors import _get_bill_decline_bill_arguments

        bill, declined_bill = self.create_bill_decline__conversion()

        actors_ids = []
        for role, actor in _get_bill_decline_bill_arguments(bill)['actors']:
            actors_ids.append((role, actor.id))
        self.assertEqual(set(actors_ids), set([(relations.ACTOR_ROLE.BILL, bill.id),
                                               (relations.ACTOR_ROLE.BILL, declined_bill.id),
                                               (relations.ACTOR_ROLE.PLACE, self.place_1.id)]))

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_bill_decline__actors_on_creation_record__conversion(self):
        bill, declined_bill = self.create_bill_decline__conversion()

        data = bill.user_form_initials
        data['approved'] = True

        form = bills_bills.bill_decline.BillDecline.ModeratorForm(data)
        self.assertTrue(form.is_valid())

        bill.update_by_moderator(form)

        self.assertTrue(bill.apply())


def create_test_create_method(record_class):

    def test_create_method(self):

        actors = []

        for role in record_class.ACTORS:
            if role.is_PLACE:
                if (role, self.place_1) not in actors:
                    actors.append((role, self.place_1))
                else:
                    actors.append((role, self.place_2))
            elif role.is_BILL:
                actors.append((role, self.bill))
            elif role.is_PERSON:
                actors.append((role, self.place_1.persons[0]))

        record = record_class(actors=actors,
                              text='xxx' if 'bill' in record_class.__name__.lower() else None)

        old_records_number = models.Record.objects.all().count()
        record.create_record()
        self.assertEqual(old_records_number + 1, models.Record.objects.all().count())

        for actor in list(zip(*actors))[1]:
            self.assertTrue(models.Actor.objects.filter(uid=prototypes.create_external_actor(actor).uid).exists())

    return test_create_method


for record_name, record_class in list(records.RECORDS.items()):
    setattr(RecordTests, 'test_' + record_name, create_test_create_method(record_class))
