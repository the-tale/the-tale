# coding: utf-8
import datetime
import jinja2

import mock

from dext.common.utils.urls import url

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic import create_test_map

from the_tale.game.heroes import logic as heroes_logic

from .. import logic
from .. import relations
from .. import conf
from .. import meta_relations



class APIListRequestTests(testcase.TestCase):

    def setUp(self):
        super(APIListRequestTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

    def test_success(self):
        self.place_2.modifier = relations.CITY_MODIFIERS.random()
        self.check_ajax_ok(self.request_ajax_json(logic.api_list_url()))


class TestShowRequests(testcase.TestCase):

    def setUp(self):
        super(TestShowRequests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('user', 'user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

    def test_place_new_place_message(self):
        self.assertTrue(self.place_1.is_new)
        self.check_html_ok(self.request_html(url('game:map:places:show', self.place_1.id)), texts=['pgf-new-place-message'])

    def test_place_new_place_message__not_new(self):
        self.place_1._model.created_at -= datetime.timedelta(seconds=conf.places_settings.NEW_PLACE_LIVETIME)
        self.place_1.save()
        self.check_html_ok(self.request_html(url('game:map:places:show', self.place_1.id)), texts=[('pgf-new-place-message', 0)])

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.is_frontier', True)
    def test_place_frontier_message(self):
        self.check_html_ok(self.request_html(url('game:map:places:show', self.place_1.id)), texts=['pgf-frontier-message'])

    @mock.patch('the_tale.game.map.places.prototypes.PlacePrototype.is_frontier', False)
    def test_place_frontier_message__not_new(self):
        self.check_html_ok(self.request_html(url('game:map:places:show', self.place_1.id)), texts=[('pgf-frontier-message', 0)])

    def test_wrong_place_id(self):
        self.check_html_ok(self.request_html(url('game:map:places:show', 'wrong_id')), texts=['pgf-error-place.wrong_format'])

    def test_place_does_not_exist(self):
        self.check_html_ok(self.request_html(url('game:map:places:show', 666)), texts=['pgf-error-place.wrong_value'])

    def check_no_heroes(self):
        texts = [('pgf-no-heroes-message', 1 + len(self.place_1.persons))]
        self.check_html_ok(self.request_html(url('game:map:places:show', self.place_1.id)), texts=texts)

    def check_heroes(self):
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        hero_1 = heroes_logic.load_hero(account_id=account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        hero_2 = heroes_logic.load_hero(account_id=account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        hero_3 = heroes_logic.load_hero(account_id=account_id)

        hero_1.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_1.preferences.set_place(self.place_1)
        hero_1.preferences.set_friend(self.place_1.persons[0])
        hero_1.preferences.set_enemy(self.place_1.persons[-1])
        heroes_logic.save_hero(hero_1)

        hero_2.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
        hero_2.preferences.set_place(self.place_1)
        hero_2.preferences.set_friend(self.place_1.persons[-1])
        hero_2.preferences.set_enemy(self.place_1.persons[0])
        heroes_logic.save_hero(hero_2)

        hero_3.preferences.set_place(self.place_1)
        hero_3.preferences.set_friend(self.place_1.persons[-1])
        hero_3.preferences.set_enemy(self.place_1.persons[0])
        heroes_logic.save_hero(hero_3)

        texts = [(jinja2.escape(hero_1.name), 3),
                 (jinja2.escape(hero_2.name), 3),
                 (jinja2.escape(hero_3.name), 0)]

        self.check_html_ok(self.request_html(url('game:map:places:show', self.place_1.id)), texts=texts)


    def test_no_heroes__unlogined(self):
        self.check_no_heroes()

    def test_no_heroes__logined(self):
        self.request_login(self.account.email)
        self.check_no_heroes()

    def test_heroes__unlogined(self):
        self.check_heroes()

    def test_heroes__logined(self):
        self.request_login(self.account.email)
        self.check_heroes()

    def test__has_folclor(self):
        from the_tale.blogs.tests import helpers as blogs_helpers

        blogs_helpers.prepair_forum()

        blogs_helpers.create_post_for_meta_object(self.account, 'folclor-1-caption', 'folclor-1-text', meta_relations.Place.create_from_object(self.place_1))
        blogs_helpers.create_post_for_meta_object(self.account, 'folclor-2-caption', 'folclor-2-text', meta_relations.Place.create_from_object(self.place_1))

        self.check_html_ok(self.request_html(url('game:map:places:show', self.place_1.id)), texts=[('pgf-no-folclor', 0),
                                                                                                   'folclor-1-caption',
                                                                                                   'folclor-2-caption'])

    def test__no_folclor(self):
        self.check_html_ok(self.request_html(url('game:map:places:show', self.place_1.id)), texts=['pgf-no-folclor'])
