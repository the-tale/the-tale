# coding: utf-8
import mock
import datetime

from contextlib import contextmanager

from dext.utils import s11n

from textgen.words import Noun

from forum.models import Post, Thread, MARKUP_METHOD

from game.bills.models import Vote
from game.bills.prototypes import BillPrototype, VotePrototype
from game.bills import bills
from game.bills.tests.prototype_tests import BaseTestPrototypes

from game.chronicle import records
from game.chronicle.models import Record, RECORD_TYPE

from game.map.places.modifiers import TradeCenter, CraftCenter

@contextmanager
def check_record_created(self, record_type):
    old_records_number = Record.objects.all().count()

    yield

    self.assertEqual(old_records_number + 1, Record.objects.all().count())
    self.assertEqual(Record.objects.all().order_by('-id')[0].type, record_type)

@mock.patch('game.bills.prototypes.BillPrototype.time_before_end_step', datetime.timedelta(seconds=0))
def process_bill(bill, success):
    with mock.patch('game.bills.prototypes.BillPrototype.is_percents_barier_not_passed', not success):
        with mock.patch('game.bills.prototypes.BillPrototype.is_votes_barier_not_passed', not success):
            bill.apply()

class BillPlaceRenamingTests(BaseTestPrototypes):

    def setUp(self):
        super(BillPlaceRenamingTests, self).setUp()

        bill_data = bills.PlaceRenaming(place_id=self.place1.id, base_name='new-name')
        self.bill = BillPrototype.create(self.account1, 'bill-caption', 'bill-rationale', bill_data)

        noun = Noun.fast_construct(self.bill.data.base_name)
        self.form = bills.PlaceRenaming.ModeratorForm({'approved': True,
                                                       'name_forms': s11n.to_json(noun.serialize()) })
        self.assertTrue(self.form.is_valid())


    def test_bill_started(self):

        with check_record_created(self, RECORD_TYPE.PLACE_CHANGE_NAME_BILL_STARTED):
            self.bill.update_by_moderator(self.form)

    def test_bill_successed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.PLACE_CHANGE_NAME_BILL_SUCCESSED):
            process_bill(self.bill, True)

    def test_bill_failed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.PLACE_CHANGE_NAME_BILL_FAILED):
            process_bill(self.bill, False)


class BillPlaceDescriptionTests(BaseTestPrototypes):

    def setUp(self):
        super(BillPlaceDescriptionTests, self).setUp()

        bill_data = bills.PlaceDescripton(place_id=self.place1.id, description='new description')
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data)

        self.form = bills.PlaceDescripton.ModeratorForm({'approved': True})
        self.assertTrue(self.form.is_valid())

    def test_bill_started(self):

        with check_record_created(self, RECORD_TYPE.PLACE_CHANGE_DESCRIPTION_BILL_STARTED):
            self.bill.update_by_moderator(self.form)

    def test_bill_successed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.PLACE_CHANGE_DESCRIPTION_BILL_SUCCESSED):
            process_bill(self.bill, True)

    def test_bill_failed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.PLACE_CHANGE_DESCRIPTION_BILL_FAILED):
            process_bill(self.bill, False)


class BillPlaceChangeModifierTests(BaseTestPrototypes):

    def setUp(self):
        super(BillPlaceChangeModifierTests, self).setUp()

        bill_data = bills.PlaceModifier(place_id=self.place1.id, modifier_id=TradeCenter.get_id(), modifier_name=TradeCenter.NAME, old_modifier_name=None)
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data)

        self.form = bills.PlaceDescripton.ModeratorForm({'approved': True})
        self.assertTrue(self.form.is_valid())

    def test_bill_started(self):
        with check_record_created(self, RECORD_TYPE.PLACE_CHANGE_MODIFIER_BILL_STARTED):
            self.bill.update_by_moderator(self.form)

    def test_bill_successed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.PLACE_CHANGE_MODIFIER_BILL_SUCCESSED):
            process_bill(self.bill, True)

    def test_bill_failed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.PLACE_CHANGE_MODIFIER_BILL_FAILED):
            process_bill(self.bill, False)

class BillPersonRemoveTests(BaseTestPrototypes):

    def setUp(self):
        super(BillPersonRemoveTests, self).setUp()

        bill_data = bills.PersonRemove(person_id=self.place1.persons[0].id, old_place_name_forms=self.place1.normalized_name)
        self.bill = BillPrototype.create(self.account1, 'bill-1-caption', 'bill-1-rationale', bill_data)

        self.form = bills.PlaceDescripton.ModeratorForm({'approved': True})
        self.assertTrue(self.form.is_valid())

    def test_bill_started(self):
        with check_record_created(self, RECORD_TYPE.PERSON_REMOVE_BILL_STARTED):
            self.bill.update_by_moderator(self.form)

    def test_bill_successed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.PERSON_REMOVE_BILL_SUCCESSED):
            process_bill(self.bill, True)

    def test_bill_failed(self):
        self.bill.update_by_moderator(self.form)
        with check_record_created(self, RECORD_TYPE.PERSON_REMOVE_BILL_FAILED):
            process_bill(self.bill, False)
