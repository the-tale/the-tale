# coding: utf-8
import mock
import datetime

from dext.utils import s11n

from textgen.words import Noun

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

# from forum.models import Post, Thread, MARKUP_METHOD
from forum.models import Category, SubCategory

from game.logic import create_test_map

from game.map.places.storage import places_storage

from game.bills.conf import bills_settings
from game.bills.bills import PlaceRenaming
from game.bills.prototypes import BillPrototype

from game.chronicle import records
from game.chronicle.models import RECORD_TYPE, Record


class RecordTests(TestCase):

    def setUp(self):
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)



        forum_category = Category.objects.create(caption='category-1', slug='category-1')
        SubCategory.objects.create(caption=bills_settings.FORUM_CATEGORY_SLUG + '-caption',
                                   slug=bills_settings.FORUM_CATEGORY_SLUG,
                                   category=forum_category)

        bill_data = PlaceRenaming(place_id=self.place_1.id, base_name='new_name')
        self.bill = BillPrototype.create(self.account, 'bill-caption', 'bill-rationale', bill_data)

    def test_records_for_every_type(self):
        types = set(RECORD_TYPE._ALL)

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
        arguments = set(record_class.ACTORS) | set(record_class.SUBSTITUTIONS)
        kwargs = {}

        if 'place' in arguments:
            kwargs['place'] = self.place_1
        if 'bill' in arguments:
            kwargs['bill'] = self.bill
        if 'person' in arguments:
            kwargs['person'] = self.place_1.persons[0]

        for index, argument in enumerate(arguments):
            if argument not in ('place', 'bill', 'person'):
                kwargs[argument] = self.create_test_word(index)

        record = record_class(**kwargs)

        old_records_number = Record.objects.all().count()
        record.create_record()
        self.assertEqual(old_records_number + 1, Record.objects.all().count())

    return test_create_method


for record_name, record_class in records.RECORDS.items():
    setattr(RecordTests, 'test_' + record_name, create_test_create_method(record_class))
