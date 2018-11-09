
import smart_imports

smart_imports.all()


class RegistrationMiddlewareTests(utils_testcase.TestCase):

    def setUp(self):
        super(RegistrationMiddlewareTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.middleware = middleware.RegistrationMiddleware(mock.Mock())
        self.referral_link = '/?%s=%d' % (conf.settings.REFERRAL_URL_ARGUMENT, self.account.id)
        self.action_link = '/?%s=action' % conf.settings.ACTION_URL_ARGUMENT

    def test_handle_referer__not_anonymous(self):
        result = self.middleware.handle_referer(self.make_request_html('/', user=self.account._model, meta={'HTTP_REFERER': 'example.com'}))
        self.assertTrue(result.is_NOT_ANONYMOUS)

    def test_handle_referer__no_referer(self):
        result = self.middleware.handle_referer(self.make_request_html('/'))
        self.assertTrue(result.is_NO_REFERER)

    def test_handle_referer__already_saved(self):
        result = self.middleware.handle_referer(self.make_request_html('/',
                                                                       session={conf.settings.SESSION_REGISTRATION_REFERER_KEY: 'example.com'},
                                                                       meta={'HTTP_REFERER': 'example.com'}))
        self.assertTrue(result.is_ALREADY_SAVED)

    def test_handle_referer__saved(self):
        result = self.middleware.handle_referer(self.make_request_html('/', meta={'HTTP_REFERER': 'example.com'}))
        self.assertTrue(result.is_SAVED)

    def test_handle_referral__not_anonymous(self):
        result = self.middleware.handle_referral(self.make_request_html(self.referral_link, user=self.account._model))
        self.assertTrue(result.is_NOT_ANONYMOUS)

    def test_handle_referral__no_referral(self):
        result = self.middleware.handle_referral(self.make_request_html('/'))
        self.assertTrue(result.is_NO_REFERRAL)

    def test_handle_referral__referral_already_in_session(self):
        result = self.middleware.handle_referral(self.make_request_html(self.referral_link,
                                                                        session={conf.settings.SESSION_REGISTRATION_REFERRAL_KEY: 666}))
        self.assertTrue(result.is_ALREADY_SAVED)

    def test_handle_referral__referral_not_in_session(self):
        result = self.middleware.handle_referral(self.make_request_html(self.referral_link))
        self.assertTrue(result.is_SAVED)

    def test_handle_action__not_anonymous(self):
        result = self.middleware.handle_action(self.make_request_html(self.action_link, user=self.account._model))
        self.assertTrue(result.is_NOT_ANONYMOUS)

    def test_handle_action__no_action(self):
        result = self.middleware.handle_action(self.make_request_html('/'))
        self.assertTrue(result.is_NO_ACTION)

    def test_handle_action__action_already_in_session(self):
        result = self.middleware.handle_action(self.make_request_html(self.action_link,
                                                                      session={conf.settings.SESSION_REGISTRATION_ACTION_KEY: 'action2'}))
        self.assertTrue(result.is_ALREADY_SAVED)

    def test_handle_action__action_not_in_session(self):
        result = self.middleware.handle_action(self.make_request_html(self.action_link))
        self.assertTrue(result.is_SAVED)


class FirstTimeVisitMiddlewareTests(utils_testcase.TestCase):

    def setUp(self):
        super(FirstTimeVisitMiddlewareTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.middleware = middleware.FirstTimeVisitMiddleware(mock.Mock())

        self.requested_url = dext_urls.url('accounts:show', self.account.id)

    def test_visit_chain(self):
        response = self.client.get(self.requested_url)

        self.assertEqual(response.client.session.get(conf.settings.SESSION_FIRST_TIME_VISIT_VISITED_KEY), True)
        self.assertEqual(response.client.session.get(conf.settings.SESSION_FIRST_TIME_VISIT_KEY), True)

        response = self.client.get(self.requested_url)

        self.assertEqual(response.client.session.get(conf.settings.SESSION_FIRST_TIME_VISIT_VISITED_KEY), True)
        self.assertEqual(response.client.session.get(conf.settings.SESSION_FIRST_TIME_VISIT_KEY), False)

        response = self.client.get(self.requested_url)

        self.assertEqual(response.client.session.get(conf.settings.SESSION_FIRST_TIME_VISIT_VISITED_KEY), True)
        self.assertEqual(response.client.session.get(conf.settings.SESSION_FIRST_TIME_VISIT_KEY), False)
