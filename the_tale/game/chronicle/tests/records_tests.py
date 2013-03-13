# coding: utf-8

from textgen.words import Fake as FakeWord

from textgen.words import Noun

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

# from forum.models import Post, Thread, MARKUP_METHOD
from forum.models import Category, SubCategory

from game.logic import create_test_map

from game.bills.conf import bills_settings
from game.bills import bills
from game.bills.prototypes import BillPrototype

from game.chronicle import records
from game.chronicle.models import RECORD_TYPE, Record, Actor
from game.chronicle.prototypes import create_external_actor


class RecordTests(TestCase):

    def setUp(self):
        super(RecordTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)



        forum_category = Category.objects.create(caption='category-1', slug='category-1')
        SubCategory.objects.create(caption=bills_settings.FORUM_CATEGORY_SLUG + '-caption',
                                   slug=bills_settings.FORUM_CATEGORY_SLUG,
                                   category=forum_category)

        bill_data = bills.PlaceRenaming(place_id=self.place_1.id, base_name='new_name')
        self.bill = BillPrototype.create(self.account, 'bill-caption', 'bill-rationale', bill_data)

    def test_records_for_every_type(self):
        types = set(RECORD_TYPE._records)

        for record_class in records.RECORDS.values():
            if record_class.TYPE in types:
                types.remove(record_class.TYPE)

        self.assertEqual(types, set())

    def create_test_word(self, index):
        return Noun(normalized='new name %d' % index,
                    forms=['new name %d %d' % (index, i) for i in xrange( Noun.FORMS_NUMBER)],
                    properties=(u'мр',))


def create_test_create_method(record_class):

    def test_create_method(self):

        actors = {}
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
            if role._is_PLACE:
                actors[role] = self.place_1
            elif role._is_BILL:
                actors[role] = self.bill
            elif role._is_PERSON:
                actors[role] = self.place_1.persons[0]

        record = record_class(actors=actors, substitutions=substitutions)

        old_records_number = Record.objects.all().count()
        record.create_record()
        self.assertEqual(old_records_number + 1, Record.objects.all().count())

        for actor in actors.values():
            self.assertTrue(Actor.objects.filter(uid=create_external_actor(actor).uid).exists())

    return test_create_method


for record_name, record_class in records.RECORDS.items():
    setattr(RecordTests, 'test_' + record_name, create_test_create_method(record_class))
