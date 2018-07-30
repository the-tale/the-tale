
import smart_imports

smart_imports.all()


def raise_exception(*argv, **kwargs):
    raise Exception('unknown error')


class TestChangeCredentialsTask(utils_testcase.TestCase):

    def setUp(self):
        super(TestChangeCredentialsTask, self).setUp()
        game_logic.create_test_map()

        self.test_account = self.accounts_factory.create_account()
        self.fast_account = self.accounts_factory.create_account(is_fast=True)

    def test_create(self):
        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru', new_password='222222', new_nick='test_nick')

        self.assertTrue(task._model.new_password != '222222')
        self.assertTrue(task._model.new_nick == 'test_nick')
        self.assertEqual(task.state, relations.CHANGE_CREDENTIALS_TASK_STATE.WAITING)
        self.assertEqual(task.account.id, self.test_account.id)
        self.assertTrue(not prototypes.AccountPrototype.get_by_id(self.test_account.id).is_fast)

        task_duplicate = prototypes.ChangeCredentialsTaskPrototype.get_by_uuid(task.uuid)

        self.assertEqual(task.id, task_duplicate.id)

    def test_create_exceptions(self):
        self.assertRaises(exceptions.MailNotSpecifiedForFastAccountError, prototypes.ChangeCredentialsTaskPrototype.create, self.fast_account, new_password='222222', new_nick='test_nick')
        self.assertRaises(exceptions.PasswordNotSpecifiedForFastAccountError, prototypes.ChangeCredentialsTaskPrototype.create, self.fast_account, new_email='fast_user@test.com', new_nick='test_nick')
        self.assertRaises(exceptions.NickNotSpecifiedForFastAccountError, prototypes.ChangeCredentialsTaskPrototype.create, self.fast_account, new_password='222222', new_email='fast_user@test.com')

    def test_email_changed(self):
        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        self.assertTrue(task.email_changed)

        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_password='222222')
        self.assertTrue(not task.email_changed)

        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_email=self.test_account.email)
        self.assertTrue(not task.email_changed)

    def test_change_credentials(self):
        task = prototypes.ChangeCredentialsTaskPrototype.create(self.fast_account, new_email='fast_user@test.ru', new_password='222222', new_nick='test_nick')

        self.assertTrue(prototypes.AccountPrototype.get_by_id(self.fast_account.id).is_fast)

        with mock.patch('the_tale.amqp_environment.environment.workers.supervisor.cmd_update_hero_with_account_data') as fake_cmd:
            postponed_task = task.change_credentials()

        self.assertNotEqual(postponed_task, None)
        self.assertEqual(fake_cmd.call_count, 0)

    def test_change_credentials_password(self):
        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_password='222222')
        postponed_task = task.change_credentials()

        self.assertNotEqual(postponed_task, None)
        self.assertEqual(post_service_models.Message.objects.all().count(), 0)

    def test_change_credentials_nick(self):
        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_nick='test_nick')

        fake_cmd = utils_fake.FakeWorkerCommand()

        with mock.patch('the_tale.amqp_environment.environment.workers.supervisor.cmd_update_hero_with_account_data') as fake_cmd:
            postponed_task = task.change_credentials()

        self.assertNotEqual(postponed_task, None)

        self.assertEqual(post_service_models.Message.objects.all().count(), 0)

        self.assertEqual(fake_cmd.call_count, 0)

        self.assertEqual(django_auth.authenticate(nick='test_nick', password='111111'), None)

    def test_change_credentials_email(self):
        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        postponed_task = task.change_credentials()
        self.assertNotEqual(postponed_task, None)
        self.assertEqual(post_service_models.Message.objects.all().count(), 0)

    def test_request_email_confirmation_exceptions(self):
        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_password='222222')
        self.assertRaises(exceptions.NewEmailNotSpecifiedError, task.request_email_confirmation)

    def test_request_email_confirmation(self):
        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        task.request_email_confirmation()
        self.assertEqual(post_service_models.Message.objects.all().count(), 1)

        task = prototypes.ChangeCredentialsTaskPrototype.create(self.fast_account, new_email='fast_user@test.com', new_password='222222', new_nick='test_nick')
        task.request_email_confirmation()
        self.assertEqual(post_service_models.Message.objects.all().count(), 2)

    def test_process_completed_state(self):
        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        task._model.state = relations.CHANGE_CREDENTIALS_TASK_STATE.PROCESSED
        task.process(utils_fake.FakeLogger())
        self.assertEqual(task._model.state, relations.CHANGE_CREDENTIALS_TASK_STATE.PROCESSED)

        task._model.state = relations.CHANGE_CREDENTIALS_TASK_STATE.UNPROCESSED
        task.process(utils_fake.FakeLogger())
        self.assertEqual(task._model.state, relations.CHANGE_CREDENTIALS_TASK_STATE.UNPROCESSED)

        task._model.state = relations.CHANGE_CREDENTIALS_TASK_STATE.ERROR
        task.process(utils_fake.FakeLogger())
        self.assertEqual(task._model.state, relations.CHANGE_CREDENTIALS_TASK_STATE.ERROR)

    def test_process_duplicated_email(self):
        duplicated_user = self.accounts_factory.create_account()
        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_email=duplicated_user.email)
        task._model.state = relations.CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT
        task.process(utils_fake.FakeLogger())
        self.assertEqual(task._model.state, relations.CHANGE_CREDENTIALS_TASK_STATE.ERROR)

    def test_process_timeout(self):
        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        task._model.created_at = datetime.datetime.fromtimestamp(0)
        task.process(utils_fake.FakeLogger())
        self.assertEqual(task.state, relations.CHANGE_CREDENTIALS_TASK_STATE.TIMEOUT)
        self.assertEqual(task._model.comment, 'timeout')
        self.assertEqual(django_auth.authenticate(nick=self.test_account.nick, password='111111').id, task.account.id)

    def test_process_waiting_and_email_confirmation(self):
        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru')
        task.process(utils_fake.FakeLogger())
        self.assertEqual(task.state, relations.CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT)
        self.assertEqual(post_service_models.Message.objects.all().count(), 1)
        self.assertEqual(django_auth.authenticate(nick=self.test_account.nick, password='111111').id, task.account.id)

    def test_process_waiting_and_password_change(self):
        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_password='222222')
        postponed_task = task.process(utils_fake.FakeLogger())
        self.assertEqual(task.state, relations.CHANGE_CREDENTIALS_TASK_STATE.CHANGING)
        self.assertNotEqual(postponed_task, None)
        self.assertEqual(django_auth.authenticate(nick=self.test_account.nick, password='111111').id, task.account.id)

    def test_process_waiting_and_nick_change(self):
        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_nick='test_nick')
        postponed_task = task.process(utils_fake.FakeLogger())
        self.assertEqual(task.state, relations.CHANGE_CREDENTIALS_TASK_STATE.CHANGING)
        self.assertNotEqual(postponed_task, None)
        self.assertEqual(django_auth.authenticate(nick=self.test_account.nick, password='111111').id, task.account.id)

    def test_process_email_sent(self):
        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru', new_password='222222')
        postponed_task = task.process(utils_fake.FakeLogger())
        self.assertEqual(postponed_task, None)
        self.assertEqual(task.state, relations.CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT)
        self.assertEqual(post_service_models.Message.objects.all().count(), 1)
        self.assertEqual(django_auth.authenticate(nick=self.test_account.nick, password='111111').id, task.account.id)
        self.assertEqual(django_auth.authenticate(nick=self.test_account.nick, password='222222'), None)

        postponed_task = task.process(utils_fake.FakeLogger())
        self.assertEqual(task.state, relations.CHANGE_CREDENTIALS_TASK_STATE.CHANGING)
        self.assertNotEqual(postponed_task, None)

    @mock.patch('the_tale.post_service.message_handlers.ChangeEmailNotificationHandler', raise_exception)
    def test_process_error(self):
        task = prototypes.ChangeCredentialsTaskPrototype.create(self.test_account, new_email='test_user@test.ru', new_password='222222')
        task.process(utils_fake.FakeLogger())
        self.assertEqual(task.state, relations.CHANGE_CREDENTIALS_TASK_STATE.ERROR)
        self.assertEqual(post_service_models.Message.objects.all().count(), 0)
