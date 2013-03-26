# coding: utf-8
import jinja2
import datetime

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, login_url

from game.logic import create_test_map

from game.chronicle import RecordPrototype as ChronicleRecordPrototype

from game.map.places.modifiers import MODIFIERS, TradeCenter
from game.map.places.prototypes import BuildingPrototype

class RequestsTestsBase(TestCase):
    def setUp(self):
        super(RequestsTestsBase, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)

        self.client = client.Client()
        self.request_login('test_user@test.com')


class IndexTests(RequestsTestsBase):

    def test_place_info_anonimouse(self):
        self.request_logout()
        self.check_redirect(reverse('game:map:'), login_url(reverse('game:map:')))

    def test_place_info_logined(self):
        self.check_html_ok(self.client.get(reverse('game:map:')))


class CellInfoTests(RequestsTestsBase):

    def test_place_info_anonimouse(self):
        self.request_logout()
        self.check_ajax_error(self.client.get(reverse('game:map:cell-info') + '?x=2&y=3', HTTP_X_REQUESTED_WITH='XMLHttpRequest'),
                              'common.login_required')

    def test_place_info_logined(self):
        self.check_html_ok(self.client.get(reverse('game:map:cell-info') + '?x=2&y=3'), texts=[('pgf-cell-debug', 0)])

    def test_place_info_logined_staff(self):
        self.account._model.is_staff = True
        self.account.save()
        self.check_html_ok(self.client.get(reverse('game:map:cell-info') + '?x=3&y=2'), texts=[('pgf-cell-debug', 3)])

    def test_place_info_no_modifier(self):
        texts = [('pgf-current-modifier-marker', 0)] + [(modifier.NAME, 1) for modifier in MODIFIERS.values()]

        self.check_html_ok(self.client.get(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

    def test_place_info_modifier(self):
        self.place_1.modifier = TradeCenter(self.place_1)
        self.place_1.save()

        texts = [('pgf-current-modifier-marker', 1)] + [(modifier.NAME, 1 if modifier != TradeCenter else 2) for modifier in MODIFIERS.values()]

        self.check_html_ok(self.client.get(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

    def test_place_info_no_freeze_time_icon(self):
        for person in self.place_1.persons:
            person._model.created_at = datetime.datetime(2000, 1, 1)
            person.save()
        texts = [('pgf-time-before-unfreeze', 0)]
        self.check_html_ok(self.client.get(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

    def test_place_info_freeze_time_icon(self):
        texts = [('pgf-time-before-unfreeze', 1)]
        person = self.place_1.persons[0]
        person._model.created_at = datetime.datetime(2000, 1, 1)
        person.save()
        self.check_html_ok(self.client.get(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

    def test_place_chronicle(self):
        texts = [jinja2.escape(record.text) for record in ChronicleRecordPrototype.get_last_actor_records(self.place_1, 1000)]
        self.check_html_ok(self.client.get(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

    def test_building(self):
        building = BuildingPrototype.create(self.place_1.persons[0])
        texts = [building.type.text, jinja2.escape(building.person.name), jinja2.escape(self.place_1.name)]
        self.check_html_ok(self.client.get(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (building.x, building.y))), texts=texts)
