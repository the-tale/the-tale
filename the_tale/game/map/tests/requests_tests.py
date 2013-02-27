# coding: utf-8
import datetime

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic import create_test_map

from game.chronicle import RecordPrototype as ChronicleRecordPrototype

from game.map.places.modifiers import MODIFIERS, TradeCenter

class TestMapRequests(TestCase):

    def setUp(self):
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)

        self.client = client.Client()
        self.request_login('test_user@test.com')

    def test_place_info_anonimouse(self):
        self.request_logout()
        self.check_ajax_error(self.client.get(reverse('game:map:cell-info') + '?x=5&y=5', HTTP_X_REQUESTED_WITH='XMLHttpRequest'),
                              'common.login_required')

    def test_place_info_logined(self):
        self.check_html_ok(self.client.get(reverse('game:map:cell-info') + '?x=5&y=5'), texts=[('pgf-cell-debug', 0)])

    def test_place_info_logined_staff(self):
        self.account.user.is_staff = True
        self.account.user.save()
        self.check_html_ok(self.client.get(reverse('game:map:cell-info') + '?x=5&y=5'), texts=[('pgf-cell-debug', 3)])

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
            person.model.created_at = datetime.datetime(2000, 1, 1)
            person.save()
        texts = [('pgf-time-before-unfreeze', 0)]
        self.check_html_ok(self.client.get(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

    def test_place_info_freeze_time_icon(self):
        texts = [('pgf-time-before-unfreeze', 1)]
        person = self.place_1.persons[0]
        person.model.created_at = datetime.datetime(2000, 1, 1)
        person.save()
        self.check_html_ok(self.client.get(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

    def test_place_chronicle(self):
        texts = [record.text for record in ChronicleRecordPrototype.get_last_actor_records(self.place_1, 1000)]
        self.check_html_ok(self.client.get(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)
