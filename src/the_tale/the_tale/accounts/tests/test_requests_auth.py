
import smart_imports

smart_imports.all()


class AuthRequestsTests(utils_testcase.TestCase):

    def setUp(self):
        super(AuthRequestsTests, self).setUp()
        game_logic.create_test_map()
        self.account = self.accounts_factory.create_account()

    def test_login_page(self):
        response = self.client.get(dext_urls.url('accounts:auth:page-login'))
        self.check_html_ok(response)

    def test_login_page_after_login(self):
        self.request_login(self.account.email)
        self.check_redirect(dext_urls.url('accounts:auth:page-login'), '/')

    def test_login_command(self):
        self.request_login(self.account.email, '111111', remember=False)
        self.assertTrue(self.client.session.get_expiry_age() < conf.settings.SESSION_REMEMBER_TIME - 10)

    def test_login__remeber(self):
        self.request_login(self.account.email, '111111', remember=True)
        self.assertTrue(self.client.session.get_expiry_age() > conf.settings.SESSION_REMEMBER_TIME - 10)

    def test_login(self):
        response = self.client.post(dext_urls.url('accounts:auth:api-login', api_version='1.0', api_client='test-1.0', next_url='/bla-bla'),
                                    {'email': self.account.email, 'password': '111111'})
        self.check_ajax_ok(response)

        data = s11n.from_json(response.content.decode('utf-8'))

        self.assertEqual(data['data']['next_url'], '/bla-bla')
        self.assertEqual(data['data']['account_id'], self.account.id)
        self.assertEqual(data['data']['account_name'], self.account.nick)
        self.assertTrue(data['data']['session_expire_at'] > time.time())

    def test_logout_command_post(self):
        self.request_logout()

    def test_logout_command_get(self):
        self.check_redirect(logic.logout_url(), '/')
