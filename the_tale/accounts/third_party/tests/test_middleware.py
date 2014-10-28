# coding: utf-8
import uuid

import mock

from django.conf import settings as project_settings

from dext.common.utils.urls import url

from the_tale.common.utils.testcase import TestCase

from the_tale.game.logic import create_test_map

from the_tale.accounts.third_party import prototypes
from the_tale.accounts.third_party import middleware
from the_tale.accounts.third_party.conf import third_party_settings


class MiddlewareTests(TestCase):

    def setUp(self):
        super(MiddlewareTests, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.middleware = middleware.ThirdPartyMiddleware()


    def test_token_not_in_session__authenticated(self):
        result = self.middleware.handle_third_party(self.make_request_html('/',
                                                                           session={},
                                                                           user=self.account_1._model))
        self.assertTrue(result.is_NO_ACCESS_TOKEN)


    def test_token_not_in_session__not_authenticated(self):
        result = self.middleware.handle_third_party(self.make_request_html('/',
                                                                           session={}))
        self.assertTrue(result.is_NO_ACCESS_TOKEN)


    def test_rejected_token__authenticated(self):
        with mock.patch('the_tale.accounts.logic.logout_user') as logout_user:
            result = self.middleware.handle_third_party(self.make_request_html('/',
                                                                            session={third_party_settings.ACCESS_TOKEN_SESSION_KEY: str(uuid.uuid4())},
                                                                            user=self.account_1._model))
        self.assertTrue(result.is_ACCESS_TOKEN_REJECTED__LOGOUT)

        self.assertEqual(logout_user.call_count, 1)


    def test_rejected_token__not_authenticated(self):
        result = self.middleware.handle_third_party(self.make_request_html('/',
                                                                           session={third_party_settings.ACCESS_TOKEN_SESSION_KEY: str(uuid.uuid4())}))
        self.assertTrue(result.is_ACCESS_TOKEN_REJECTED)


    def test_token_not_accepted_yet__authenticated(self):
        token = prototypes.AccessTokenPrototype.fast_create(id=1)

        with mock.patch('the_tale.accounts.logic.logout_user') as logout_user:
            result = self.middleware.handle_third_party(self.make_request_html('/',
                                                                            session={third_party_settings.ACCESS_TOKEN_SESSION_KEY: token.uid},
                                                                            user=self.account_1._model))

        self.assertTrue(result.is_ACCESS_TOKEN_NOT_ACCEPTED_YET)
        self.assertEqual(logout_user.call_count, 1)


    def test_token_not_accepted_yet__not_authenticated(self):
        token = prototypes.AccessTokenPrototype.fast_create(id=1)

        with mock.patch('the_tale.accounts.logic.logout_user') as logout_user:
            result = self.middleware.handle_third_party(self.make_request_html('/',
                                                                            session={third_party_settings.ACCESS_TOKEN_SESSION_KEY: token.uid}))

        self.assertTrue(result.is_ACCESS_TOKEN_NOT_ACCEPTED_YET)
        self.assertEqual(logout_user.call_count, 0)

    def test_no_cache(self):
        token = prototypes.AccessTokenPrototype.fast_create(id=1, account=self.account_1)

        with mock.patch('dext.common.utils.cache.set') as set_cache:
            with mock.patch('the_tale.accounts.logic.force_login_user'):
                self.middleware.handle_third_party(self.make_request_html('/',
                                                                        session={third_party_settings.ACCESS_TOKEN_SESSION_KEY: token.uid}))

        cache_key = third_party_settings.ACCESS_TOKEN_CACHE_KEY % token.uid

        self.assertEqual(set_cache.call_args_list, [mock.call(cache_key, token.cache_data(), third_party_settings.ACCESS_TOKEN_CACHE_TIMEOUT)])


    def test_authenticated(self):
        token = prototypes.AccessTokenPrototype.fast_create(id=1, account=self.account_1)

        with mock.patch('the_tale.accounts.logic.force_login_user') as force_login_user:
            result = self.middleware.handle_third_party(self.make_request_html('/',
                                                                           session={third_party_settings.ACCESS_TOKEN_SESSION_KEY: token.uid},
                                                                           user=self.account_1._model))
        self.assertTrue(result.is_ACCESS_TOKEN_ACCEPTED)
        self.assertEqual(force_login_user.call_count, 0)


    def test_authenticated_by_another_user(self):
        token = prototypes.AccessTokenPrototype.fast_create(id=1, account=self.account_1)

        account_2 = self.accounts_factory.create_account()

        with mock.patch('the_tale.accounts.logic.force_login_user') as force_login_user:
            result = self.middleware.handle_third_party(self.make_request_html('/',
                                                                           session={third_party_settings.ACCESS_TOKEN_SESSION_KEY: token.uid},
                                                                           user=account_2._model))
        self.assertTrue(result.is_ACCESS_TOKEN_ACCEPTED__USER_LOGED_IN)

        self.assertEqual(force_login_user.call_count, 1)


    def test_not_authenticated(self):
        token = prototypes.AccessTokenPrototype.fast_create(id=1, account=self.account_1)

        with mock.patch('the_tale.accounts.logic.force_login_user') as force_login_user:
            result = self.middleware.handle_third_party(self.make_request_html('/',
                                                                               session={third_party_settings.ACCESS_TOKEN_SESSION_KEY: token.uid}))
        self.assertTrue(result.is_ACCESS_TOKEN_ACCEPTED__USER_LOGED_IN)

        self.assertEqual(force_login_user.call_count, 1)



class MiddlewareRequestsTests(TestCase):

    def setUp(self):
        super(MiddlewareRequestsTests, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.request_token_url = url('accounts:third-party:tokens:request-authorisation', api_version='1.0', api_client=project_settings.API_CLIENT)

    def do_test_request(self):
        self.request_html('/')

    def do_token_request(self):
        self.check_ajax_ok(self.client.post(self.request_token_url, {'application_name': 'app-name',
                                                                     'application_info': 'app-info',
                                                                     'application_description': 'app-descr'}))

    def test_token_not_in_session__authenticated(self):
        self.request_login(self.account_1.email)

        self.do_test_request()

        self.assertFalse(third_party_settings.ACCESS_TOKEN_SESSION_KEY in self.client.session)


    def test_token_not_in_session__not_authenticated(self):
        self.do_test_request()

        self.assertFalse(third_party_settings.ACCESS_TOKEN_SESSION_KEY in self.client.session)


    def test_rejected_token__authenticated(self):
        self.request_login(self.account_1.email)

        self.do_token_request()

        prototypes.AccessTokenPrototype._db_latest().remove()

        self.check_logged_in()

        self.do_test_request()

        self.check_logged_out()

        self.assertIn(third_party_settings.ACCESS_TOKEN_SESSION_KEY, self.client.session)

    def test_rejected_token__not_authenticated(self):

        self.do_token_request()

        prototypes.AccessTokenPrototype._db_latest().remove()

        self.do_test_request()

        self.check_logged_out()

        self.assertIn(third_party_settings.ACCESS_TOKEN_SESSION_KEY, self.client.session)


    def test_token_not_accepted_yet__authenticated(self):

        self.request_login(self.account_1.email)

        self.do_token_request()

        self.check_logged_in()

        self.do_test_request()

        self.check_logged_out()

        self.assertIn(third_party_settings.ACCESS_TOKEN_SESSION_KEY, self.client.session)


    def test_token_not_accepted_yet__not_authenticated(self):

        self.do_token_request()

        self.do_test_request()

        self.check_logged_out()

        self.assertIn(third_party_settings.ACCESS_TOKEN_SESSION_KEY, self.client.session)


    def test_no_cache(self):
        self.do_token_request()

        token = prototypes.AccessTokenPrototype._db_latest()

        token.accept(self.account_1)

        with mock.patch('dext.common.utils.cache.set') as set_cache:
            self.do_test_request()

        cache_key = third_party_settings.ACCESS_TOKEN_CACHE_KEY % token.uid

        self.assertEqual(set_cache.call_args_list, [mock.call(cache_key, token.cache_data(), third_party_settings.ACCESS_TOKEN_CACHE_TIMEOUT)])

        self.check_logged_in()


    def test_authenticated_by_another_user(self):
        account_2 = self.accounts_factory.create_account()

        self.request_login(account_2.email)

        self.do_token_request()

        token = prototypes.AccessTokenPrototype._db_latest()

        token.accept(self.account_1)

        self.do_test_request()

        self.check_logged_in(account=self.account_1)

        self.assertIn(third_party_settings.ACCESS_TOKEN_SESSION_KEY, self.client.session)


    def test_not_authenticated(self):
        self.do_token_request()

        token = prototypes.AccessTokenPrototype._db_latest()

        token.accept(self.account_1)

        self.do_test_request()

        self.check_logged_in(account=self.account_1)

        self.assertIn(third_party_settings.ACCESS_TOKEN_SESSION_KEY, self.client.session)
