# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse

from dext.utils import s11n

from textgen.words import Noun

from common.utils.testcase import TestCase
from common.utils.permissions import sync_group

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, login_url

from game.logic import create_test_map

from game.chronicle.models import RECORD_TYPE, Record
from game.chronicle.records import RecordBase
from game.chronicle.conf import chronicle_settings


class FakeRecord(RecordBase):
    def __init__(self, type_, index, turn_number):
        self.TYPE = type_
        self.index = index
        self.created_at_turn = turn_number

    def get_text(self): return 'record_text_%d_%d' % (self.created_at_turn, self.index)



class IndexRequestsTest(TestCase):

    def setUp(self):
        create_test_map()

        Record.objects.all().delete()

        self.client = client.Client()

    def create_record(self, index, turn_number=0, type_=RECORD_TYPE.PLACE_CHANGE_RACE):
        FakeRecord(type_=type_, index=index, turn_number=turn_number).create_record()

    def test_no_records(self):
        self.check_html_ok(self.client.get(reverse('game:chronicle:')), texts=['pgf-no-records-message'])

    def test_success(self):
        self.create_record(0)
        self.check_html_ok(self.client.get(reverse('game:chronicle:')), texts=['record_text_0_0'])

    def test_full_page(self):
        texts = []
        for i in xrange(chronicle_settings.RECORDS_ON_PAGE):
            self.create_record(i)
            texts.append('record_text_%d_%d' % (0, i))

        self.check_html_ok(self.client.get(reverse('game:chronicle:')), texts=texts)
        self.check_redirect(reverse('game:chronicle:')+'?page=2', reverse('game:chronicle:')+'?page=1')

    def test_second_page(self):
        for i in xrange(chronicle_settings.RECORDS_ON_PAGE+1):
            self.create_record(i)

        texts = ['record_text_%d_%d' % (0, chronicle_settings.RECORDS_ON_PAGE)]

        self.check_html_ok(self.client.get(reverse('game:chronicle:')+'?page=2'), texts=texts)
