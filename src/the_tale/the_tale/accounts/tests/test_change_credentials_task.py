
import smart_imports

smart_imports.all()


class PostponedChangeCredentialsTaskTests(utils_testcase.TestCase):

    def setUp(self):
        super(PostponedChangeCredentialsTaskTests, self).setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.task = prototypes.ChangeCredentialsTaskPrototype.create(self.account,
                                                                     new_email='test_user@test.ru',
                                                                     new_password='222222',
                                                                     new_nick='test_nick',
                                                                     relogin_required=True)

        self.postponed_task = postponed_tasks.ChangeCredentials(task_id=self.task.id)

    def test_create(self):
        self.assertEqual(self.postponed_task.processed_data, {'next_url': dext_urls.url('accounts:profile:edited')})
        self.assertEqual(self.postponed_task.task_id, self.task.id)
        self.assertTrue(self.postponed_task.state.is_UNPROCESSED)

    def test_serialization(self):
        self.assertEqual(self.postponed_task.serialize(), postponed_tasks.ChangeCredentials.deserialize(self.postponed_task.serialize()).serialize())

    def test_processed_view__real(self):
        self.assertEqual(self.task.process(logger=mock.Mock()), None)  # sent mail
        postponed_taks = self.task.process(logger=mock.Mock())  # create task
        postponed_taks.process(logger=mock.Mock())
        self.check_ajax_ok(self.client.get(dext_urls.url('postponed-tasks:status', postponed_taks.id)))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_processed_view__logout__same_user(self):
        self.request_login(self.account.email)

        self.assertEqual(self.task.process(logger=mock.Mock()), None)  # sent mail
        postponed_taks = self.task.process(logger=mock.Mock())  # create task
        postponed_taks.process(logger=mock.Mock())
        self.check_ajax_ok(self.client.get(dext_urls.url('postponed-tasks:status', postponed_taks.id)))

        self.assertNotIn('_auth_user_id', self.client.session)

    def test_processed_view__logout__other_user(self):
        account_2 = self.accounts_factory.create_account()

        self.request_login(account_2.email)

        self.assertEqual(self.task.process(logger=mock.Mock()), None)  # sent mail
        postponed_taks = self.task.process(logger=mock.Mock())  # create task
        postponed_taks.process(logger=mock.Mock())
        self.check_ajax_ok(self.client.get(dext_urls.url('postponed-tasks:status', postponed_taks.id)))

        self.assertEqual(int(self.client.session.get('_auth_user_id')), account_2.id)

    def test_processed_view__real__without_relogin(self):
        self.task._model.relogin_required = False
        self.task._model.save()

        self.assertEqual(self.task.process(logger=mock.Mock()), None)  # sent mail
        postponed_taks = self.task.process(logger=mock.Mock())  # create task
        postponed_taks.process(logger=mock.Mock())
        self.check_ajax_ok(self.client.get(dext_urls.url('postponed-tasks:status', postponed_taks.id)))
        self.assertEqual(self.client.session.get('_auth_user_id'), None)

    def test_process__wrong_state(self):
        self.postponed_task.state = postponed_tasks.CHANGE_CREDENTIALS_STATE.PROCESSED
        self.assertEqual(self.postponed_task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertTrue(self.postponed_task.state.is_WRONG_STATE)

    def test_process(self):
        self.assertEqual(self.postponed_task.process(main_task=mock.Mock()), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertTrue(self.postponed_task.state.is_PROCESSED)
        self.assertEqual(django_auth.authenticate(nick='test_nick', password='222222').email, 'test_user@test.ru')
