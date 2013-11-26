# coding: utf-8
import mock
import datetime
from textgen.words import Fake as FakeWord

from textgen.words import Noun

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.forum.models import Category, SubCategory

from the_tale.game.logic import create_test_map

from the_tale.game.bills.conf import bills_settings
from the_tale.game.bills import bills
from the_tale.game.bills.prototypes import BillPrototype
from the_tale.game.bills.tests.helpers import choose_resources

from the_tale.game.chronicle import records
from the_tale.game.chronicle.models import RECORD_TYPE, Record, Actor
from the_tale.game.chronicle.prototypes import create_external_actor
from the_tale.game.chronicle.relations import ACTOR_ROLE


class RecordTests(TestCase):

    def setUp(self):
        super(RecordTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        forum_category = Category.objects.create(caption='category-1', slug='category-1')
        SubCategory.objects.create(caption=bills_settings.FORUM_CATEGORY_UID + '-caption',
                                   uid=bills_settings.FORUM_CATEGORY_UID,
                                   category=forum_category)

        bill_data = bills.PlaceRenaming(place_id=self.place_1.id, base_name='new_name')
        self.bill = BillPrototype.create(self.account, 'bill-caption', 'bill-rationale', bill_data)

    def test_records_for_every_type(self):
        types = set(RECORD_TYPE.records)

        for record_class in records.RECORDS.values():
            if record_class.TYPE in types:
                types.remove(record_class.TYPE)

        self.assertEqual(types, set())

    def create_test_word(self, index):
        return Noun(normalized='new name %d' % index,
                    forms=['new name %d %d' % (index, i) for i in xrange( Noun.FORMS_NUMBER)],
                    properties=(u'мр',))

    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def create_bill_decline(self):
        resource_1, resource_2 = choose_resources()

        declined_bill_data = bills.PlaceResourceExchange(place_1_id=self.place_1.id,
                                                         place_2_id=self.place_2.id,
                                                         resource_1=resource_1,
                                                         resource_2=resource_2)

        declined_bill = BillPrototype.create(self.account, 'declined-bill-caption', 'declined-bill-rationale', declined_bill_data)

        declined_form = bills.PlaceResourceExchange.ModeratorForm({'approved': True})
        self.assertTrue(declined_form.is_valid())
        declined_bill.update_by_moderator(declined_form)
        declined_bill.apply()

        bill_data = bills.BillDecline(declined_bill_id=declined_bill.id)
        bill = BillPrototype.create(self.account, 'bill-caption', 'bill-rationale', bill_data)
        return bill, declined_bill

    def test_bill_decline__actors(self):
        from the_tale.game.chronicle.signal_processors import _get_bill_decline_bill_arguments

        bill, declined_bill = self.create_bill_decline()

        actors_ids = []
        for role, actor in _get_bill_decline_bill_arguments(bill)['actors']:
            actors_ids.append((role, actor.id))
        self.assertEqual(sorted(actors_ids), sorted([(ACTOR_ROLE.BILL, bill.id),
                                                     (ACTOR_ROLE.BILL, declined_bill.id),
                                                     (ACTOR_ROLE.PLACE, self.place_1.id),
                                                     (ACTOR_ROLE.PLACE, self.place_2.id)]))

    @mock.patch('the_tale.game.bills.conf.bills_settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    def test_bill_decline__actors_on_creation_record(self):
        bill, declined_bill = self.create_bill_decline()
        form = bills.BillDecline.ModeratorForm({'approved': True})
        self.assertTrue(form.is_valid())

        bill.update_by_moderator(form)

        self.assertTrue(bill.apply())



def create_test_create_method(record_class):

    def test_create_method(self):

        actors = []
        substitutions = {}

        for index, argument in enumerate(record_class.SUBSTITUTIONS):
            if 'place' == argument:
                substitutions['place'] = self.place_1
            elif 'bill' == argument:
                substitutions['bill'] = FakeWord(self.bill.caption)
            elif 'person' == argument:
                substitutions['person'] = self.place_1.persons[0]
            else:
                substitutions[argument] = self.create_test_word(index)

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

        record = record_class(actors=actors, substitutions=substitutions)

        old_records_number = Record.objects.all().count()
        record.create_record()
        self.assertEqual(old_records_number + 1, Record.objects.all().count())

        for actor in zip(*actors)[1]:
            self.assertTrue(Actor.objects.filter(uid=create_external_actor(actor).uid).exists())

    return test_create_method


for record_name, record_class in records.RECORDS.items():
    setattr(RecordTests, 'test_' + record_name, create_test_create_method(record_class))
