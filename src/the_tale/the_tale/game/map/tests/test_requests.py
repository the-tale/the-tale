# coding: utf-8
import jinja2
import datetime

from unittest import mock

from django.test import client
from django.core.urlresolvers import reverse

from dext.common.utils.urls import url

from the_tale.common.utils.testcase import TestCase

from the_tale.game import names
from the_tale.game.balance import constants as c

from the_tale.game.logic import create_test_map

from the_tale.game.prototypes import TimePrototype

from the_tale.game.chronicle.prototypes import RecordPrototype as ChronicleRecordPrototype

from the_tale.game.persons import logic as persons_logic
from the_tale.game.persons import models as persons_models
from the_tale.game.persons import storage as persons_storage

from the_tale.game.places import modifiers as places_modifiers
from the_tale.game.places import conf as places_conf
from the_tale.game.places import logic as places_logic
from the_tale.game.places import models as places_models
from the_tale.game.places import storage as places_storage

from the_tale.game.map.conf import map_settings

from ..generator import update_map
from .. import logic


class RequestsTestsBase(TestCase):
    def setUp(self):
        super(RequestsTestsBase, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.account = self.accounts_factory.create_account()

        self.client = client.Client()
        self.request_login(self.account.email)


class IndexTests(RequestsTestsBase):

    def test_success(self):
        self.check_html_ok(self.request_html(reverse('game:map:')))


class CellInfoTests(RequestsTestsBase):

    def test_place_info_logined(self):
        self.check_html_ok(self.request_html(reverse('game:map:cell-info') + '?x=2&y=3'), texts=[])

    def test_place_info_no_modifier(self):
        texts = [('pgf-current-modifier-marker', 0)]
        self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)


    @mock.patch('the_tale.game.persons.objects.Person.on_move_timeout', False)
    def test_place_info_no_freeze_time_icon(self):
        texts = [('pgf-time-before-unfreeze', 0)]
        self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)


    @mock.patch('the_tale.game.persons.objects.Person.on_move_timeout', True)
    def test_place_info_freeze_time_icon(self):
        texts = ['pgf-time-before-unfreeze']
        self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

    def test_place_new_place_message(self):
        self.assertTrue(self.place_1.is_new)
        self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=['pgf-new-place-message'])

    def test_place_new_place_message__not_new(self):
        places_models.Place.objects.filter(id=self.place_1.id).update(created_at=datetime.datetime(2000, 1, 1))
        places_storage.places.refresh()

        self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=[('pgf-new-place-message', 0)])

    @mock.patch('the_tale.game.places.objects.Place.is_frontier', True)
    def test_place_frontier_message(self):
        self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=['pgf-frontier-message'])

    @mock.patch('the_tale.game.places.objects.Place.is_frontier', False)
    def test_place_frontier_message__not_new(self):
        self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=[('pgf-frontier-message', 0)])


    def test_place_chronicle(self):
        texts = [jinja2.escape(record.text) for record in ChronicleRecordPrototype.get_last_actor_records(self.place_1, 1000)]
        self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

    def test_building(self):
        building = places_logic.create_building(self.place_1.persons[0], utg_name=names.generator().get_test_name('building-name'))
        texts = [building.type.text, jinja2.escape(building.person.name), jinja2.escape(self.place_1.name)]
        self.check_html_ok(self.request_html(reverse('game:map:cell-info') + ('?x=%d&y=%d' % (building.x, building.y))), texts=texts)

    def test_outside_map(self):
        self.check_html_ok(self.request_html(url('game:map:cell-info', x=0, y=0)), texts=[('outside_map', 0)])
        self.check_html_ok(self.request_html(url('game:map:cell-info', x=map_settings.WIDTH-1, y=map_settings.HEIGHT-1)), texts=[('outside_map', 0)])

        self.check_html_ok(self.request_html(url('game:map:cell-info', x=-1, y=0)), texts=[('outside_map', 1)])
        self.check_html_ok(self.request_html(url('game:map:cell-info', x=0, y=-1)), texts=[('outside_map', 1)])
        self.check_html_ok(self.request_html(url('game:map:cell-info', x=map_settings.WIDTH, y=map_settings.HEIGHT-1)), texts=[('outside_map', 1)])
        self.check_html_ok(self.request_html(url('game:map:cell-info', x=map_settings.WIDTH-1, y=map_settings.HEIGHT)), texts=[('outside_map', 1)])



class RegionTests(RequestsTestsBase):

    def setUp(self):
        super(RegionTests, self).setUp()
        update_map(index=0)

    def test_last(self):
        self.check_ajax_ok(self.request_ajax_json(logic.region_url()))


    def test_no_region_for_turn(self):
        self.check_ajax_error(self.request_ajax_json(logic.region_url(666)), 'no_region_found')


    def test_region_for_turn(self):
        current_time = TimePrototype.get_current_time()
        current_time.increment_turn()

        self.check_ajax_error(self.request_ajax_json(logic.region_url(current_time.get_current_turn_number())), 'no_region_found')

        update_map(index=1)

        self.check_ajax_ok(self.request_ajax_json(logic.region_url(current_time.get_current_turn_number())))



class RegionVersionsTests(RequestsTestsBase):

    def setUp(self):
        super(RegionVersionsTests, self).setUp()
        update_map(index=0)

    def test_region_for_turn(self):

        current_time = TimePrototype.get_current_time()

        turn = current_time.get_current_turn_number()

        self.check_ajax_ok(self.request_ajax_json(logic.region_versions_url()), {'turns': [turn]})

        current_time.increment_turn()

        self.check_ajax_ok(self.request_ajax_json(logic.region_versions_url()), {'turns': [turn]})

        update_map(index=1)

        self.check_ajax_ok(self.request_ajax_json(logic.region_versions_url()), {'turns': [turn, turn+1]})
