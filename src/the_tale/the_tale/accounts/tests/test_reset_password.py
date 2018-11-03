
import smart_imports

smart_imports.all()


def raise_exception(*argv, **kwargs):
    raise Exception('unknown error')


class ResetPasswordTaskTests(utils_testcase.TestCase):

    def setUp(self):
        super(ResetPasswordTaskTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.task = prototypes.ResetPasswordTaskPrototype.create(self.account)

    # change methods order to prevent segmentation fault
    def test_2_create(self):
        self.assertEqual(post_service_models.Message.objects.all().count(), 1)
        self.assertEqual(models.ResetPasswordTask.objects.all().count(), 1)

    def test_1_process(self):
        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(prototypes.ChangeCredentialsTaskPrototype._model_class.objects.all().count(), 0)

        new_password = self.task.process(logger=mock.Mock())
        self.assertTrue(self.task.is_processed)
        self.assertEqual(django_auth.authenticate(nick=self.account.nick, password='111111').id, self.account.id)

        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 1)
        self.assertEqual(prototypes.ChangeCredentialsTaskPrototype._model_class.objects.all().count(), 1)

        PostponedTaskPrototype._db_get_object(0).process(logger=mock.Mock())

        self.assertEqual(django_auth.authenticate(nick=self.account.nick, password='111111'), None)
        self.assertEqual(django_auth.authenticate(nick=self.account.nick, password=new_password).id, self.account.id)


class ResetPasswordRequestsTests(utils_testcase.TestCase):

    def setUp(self):
        super(ResetPasswordRequestsTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

    def test_reset_password_page_for_loggined_user(self):
        chronicle_tt_services.chronicle.cmd_debug_clear_service()

        self.request_login(self.account.email)
        self.check_redirect(django_reverse('accounts:profile:reset-password'), '/')

    def test_reset_password_page(self):
        self.check_html_ok(self.request_html(django_reverse('accounts:profile:reset-password')))

    def test_reset_password_page_for_wrong_email(self):
        self.check_ajax_error(self.client.post(django_reverse('accounts:profile:reset-password'), {'email': 'wrong@test.com'}), 'accounts.profile.reset_password.wrong_email')
        self.assertEqual(django_auth.authenticate(nick=self.account.nick, password='111111').id, self.account.id)
        self.assertEqual(models.ResetPasswordTask.objects.all().count(), 0)

    def test_reset_password_success(self):
        self.check_ajax_ok(self.client.post(django_reverse('accounts:profile:reset-password'), {'email': self.account.email}))
        self.assertEqual(django_auth.authenticate(nick=self.account.nick, password='111111').id, self.account.id)
        self.assertEqual(models.ResetPasswordTask.objects.all().count(), 1)

    def test_reset_password_done(self):
        self.check_html_ok(self.request_html(django_reverse('accounts:profile:reset-password-done')))

    def test_reset_password_processed(self):
        task = prototypes.ResetPasswordTaskPrototype.create(self.account)

        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 0)
        self.assertEqual(prototypes.ChangeCredentialsTaskPrototype._model_class.objects.all().count(), 0)

        self.check_html_ok(self.request_html(django_reverse('accounts:profile:reset-password-processed') + ('?task=%s' % task.uuid)))

        self.assertEqual(PostponedTaskPrototype._model_class.objects.all().count(), 1)
        self.assertEqual(prototypes.ChangeCredentialsTaskPrototype._model_class.objects.all().count(), 1)

        self.assertEqual(django_auth.authenticate(nick=self.account.nick, password='111111').id, self.account.id)

    def test_reset_password_expired(self):
        task = prototypes.ResetPasswordTaskPrototype.create(self.account)
        with mock.patch('the_tale.accounts.conf.settings.RESET_PASSWORD_TASK_LIVE_TIME', -1):
            self.check_html_ok(self.request_html(django_reverse('accounts:profile:reset-password-processed') + ('?task=%s' % task.uuid)),
                               texts=['accounts.profile.reset_password_processed.time_expired'])
        self.assertEqual(django_auth.authenticate(nick=self.account.nick, password='111111').id, self.account.id)

    def test_reset_password_already_processed(self):
        task = prototypes.ResetPasswordTaskPrototype.create(self.account)
        self.check_html_ok(self.request_html(django_reverse('accounts:profile:reset-password-processed') + ('?task=%s' % task.uuid)))
        self.check_html_ok(self.request_html(django_reverse('accounts:profile:reset-password-processed') + ('?task=%s' % task.uuid)),
                           texts=['accounts.profile.reset_password_processed.already_processed'])
