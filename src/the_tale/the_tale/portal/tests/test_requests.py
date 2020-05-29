
import smart_imports

smart_imports.all()


class TestRequests(utils_testcase.TestCase):

    def setUp(self):
        super(TestRequests, self).setUp()
        game_logic.create_test_map()

        chronicle_tt_services.chronicle.cmd_debug_clear_service()

    def test_search(self):
        self.check_html_ok(self.request_html(utils_urls.url('portal:search')))

    def test_chat(self):
        self.check_html_ok(self.request_html(utils_urls.url('portal:chat')))

    def test_chat_bind_discord__unlogined(self):
        self.check_html_ok(self.request_ajax_html(utils_urls.url('portal:chat-bind-discord')),
                           texts=['common.login_required'])

    def test_chat_bind_discord(self):
        account = self.accounts_factory.create_account()
        self.request_login(account.email)

        self.check_html_ok(self.request_html(utils_urls.url('portal:chat-bind-discord')))

    def test_preview(self):
        text = 'simple test text'
        self.check_html_ok(self.client.post(utils_urls.url('portal:preview'), {'text': text}), texts=[text])

    def test_hot_themes__show_all(self):
        forum = forum_helpers.ForumFixture(self.accounts_factory)
        self.check_html_ok(self.request_html(utils_urls.url('portal:')), texts=[forum.thread_1.caption, forum.thread_2.caption, forum.thread_3.caption])

    def test_hot_themes__hide_restricted_themes(self):
        forum = forum_helpers.ForumFixture(self.accounts_factory)
        forum.subcat_3._model.restricted = True
        forum.subcat_3.save()
        self.check_html_ok(self.request_html(utils_urls.url('portal:')), texts=[forum.thread_1.caption, forum.thread_2.caption, (forum.thread_3.caption, 0)])

    def test_info(self):
        self.check_ajax_ok(self.request_json(utils_urls.url('portal:api-info', api_version='1.0', api_client=django_settings.API_CLIENT)),
                           data={'static_content': django_settings.STATIC_URL,
                                 'game_version': django_settings.META_CONFIG.version,
                                 'turn_delta': c.TURN_DELTA,
                                 'account_id': None,
                                 'account_name': None,
                                 'abilities_cost': {ability_type.value: ability_type.cost for ability_type in abilities_relations.ABILITY_TYPE.records}})

    def test_info__logined(self):
        account = self.accounts_factory.create_account()
        self.request_login(account.email)

        self.check_ajax_ok(self.request_json(utils_urls.url('portal:api-info', api_version='1.0', api_client=django_settings.API_CLIENT)),
                           data={'static_content': django_settings.STATIC_URL,
                                 'game_version': django_settings.META_CONFIG.version,
                                 'turn_delta': c.TURN_DELTA,
                                 'account_id': account.id,
                                 'account_name': account.nick,
                                 'abilities_cost': {ability_type.value: ability_type.cost for ability_type in abilities_relations.ABILITY_TYPE.records}})


class IndexRequestTests(utils_testcase.TestCase):

    def setUp(self):
        super(IndexRequestTests, self).setUp()
        game_logic.create_test_map()

        chronicle_tt_services.chronicle.cmd_debug_clear_service()

    def test_success(self):
        response = self.client.get(utils_urls.url('portal:'))
        self.assertEqual(response.status_code, 200)

    def test_first_time(self):
        with mock.patch('the_tale.accounts.logic.is_first_time_visit', lambda request: True):
            self.check_html_ok(self.request_html('/'), texts=[('pgf-first-time-introduction', 1)])

        with mock.patch('the_tale.accounts.logic.is_first_time_visit', lambda request: False):
            self.check_html_ok(self.request_html('/'), texts=[('pgf-first-time-introduction', 0)])
