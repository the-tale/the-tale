
import smart_imports

smart_imports.all()


class MightDataTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.accounts = [self.accounts_factory.create_account()
                         for _ in range(2)]

    def test_no_records__collect(self):
        report = data_protection.collect_might_data(self.accounts[0].id)
        self.assertEqual(report, [])

    def test_no_records__remove(self):
        data_protection.remove_might_data(self.accounts[0].id)

    def prepair_data(self):
        return [models.Award.objects.create(account=self.accounts[0]._model,
                                            type=relations.AWARD_TYPE.BUG_MINOR,
                                            description='descr 1'),
                models.Award.objects.create(account=self.accounts[1]._model,
                                            type=relations.AWARD_TYPE.CONTEST_2_PLACE,
                                            description='descr 2'),
                models.Award.objects.create(account=self.accounts[0]._model,
                                            type=relations.AWARD_TYPE.STANDARD_NORMAL,
                                            description='descr 3')]

    def test_has_records__collect(self):
        records = self.prepair_data()

        report = data_protection.collect_might_data(self.accounts[0].id)

        self.assertCountEqual(report, [('mights', {'type': relations.AWARD_TYPE.BUG_MINOR,
                                                   'description': 'descr 1',
                                                   'created_at': records[0].created_at,
                                                   'updated_at': records[0].updated_at}),
                                       ('mights', {'type': relations.AWARD_TYPE.STANDARD_NORMAL,
                                                   'description': 'descr 3',
                                                   'created_at': records[2].created_at,
                                                   'updated_at': records[2].updated_at})])

    def test_has_records__remove(self):
        records = self.prepair_data()

        data_protection.remove_might_data(self.accounts[0].id)

        report = data_protection.collect_might_data(self.accounts[0].id)

        self.assertCountEqual(report, [])

        report = data_protection.collect_might_data(self.accounts[1].id)

        self.assertCountEqual(report, [('mights', {'type': relations.AWARD_TYPE.CONTEST_2_PLACE,
                                                   'description': 'descr 2',
                                                   'created_at': records[1].created_at,
                                                   'updated_at': records[1].updated_at})])


class ResetPasswordDataTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.accounts = [self.accounts_factory.create_account()
                         for _ in range(2)]

    def test_no_records__collect(self):
        report = data_protection.collect_reset_password_data(self.accounts[0].id)
        self.assertEqual(report, [])

    def test_no_records__remove(self):
        data_protection.remove_reset_password_data(self.accounts[0].id)

    def prepair_data(self):
        records = [prototypes.ResetPasswordTaskPrototype.create(self.accounts[0]),
                   prototypes.ResetPasswordTaskPrototype.create(self.accounts[1]),
                   prototypes.ResetPasswordTaskPrototype.create(self.accounts[0])]

        records[0].process()

        return records

    def test_has_records__collect(self):
        records = self.prepair_data()

        report = data_protection.collect_reset_password_data(self.accounts[0].id)

        self.assertCountEqual(report, [('reset_password', {'created_at': records[0]._model.created_at,
                                                           'is_processed': True}),
                                       ('reset_password', {'created_at': records[2]._model.created_at,
                                                           'is_processed': False})])

    def test_has_records__remove(self):
        records = self.prepair_data()

        data_protection.remove_reset_password_data(self.accounts[0].id)

        report = data_protection.collect_reset_password_data(self.accounts[0].id)

        self.assertCountEqual(report, [])

        report = data_protection.collect_reset_password_data(self.accounts[1].id)

        self.assertCountEqual(report, [('reset_password', {'created_at': records[1]._model.created_at,
                                                           'is_processed': False})])


class ChangeCredentialsDataTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.accounts = [self.accounts_factory.create_account()
                         for _ in range(2)]

    def test_no_records__collect(self):
        report = data_protection.collect_change_credentials_data(self.accounts[0].id)
        self.assertEqual(report, [])

    def test_no_records__remove(self):
        data_protection.remove_change_credentials_data(self.accounts[0].id)

    def prepair_data(self):
        tasks = [prototypes.ChangeCredentialsTaskPrototype.create(account=self.accounts[0],
                                                                  new_email='new-email-1@xxx.yyy',
                                                                  new_password='123',
                                                                  new_nick='new-nick-1'),
                 prototypes.ChangeCredentialsTaskPrototype.create(account=self.accounts[1],
                                                                  new_email='new-email-2@xxx.yyy',
                                                                  new_password='1234',
                                                                  new_nick='new-nick-2'),
                 prototypes.ChangeCredentialsTaskPrototype.create(account=self.accounts[0],
                                                                  new_email='new-email-3@xxx.yyy',
                                                                  new_password='12345',
                                                                  new_nick='new-nick-3')]

        tasks[0].change_credentials()

        return tasks

    def test_has_records__collect(self):

        tasks = self.prepair_data()

        report = data_protection.collect_change_credentials_data(self.accounts[0].id)

        self.assertCountEqual(report,
                              [('change_credentials', {'created_at': tasks[0].created_at,
                                                       'updated_at': tasks[0].updated_at,
                                                       'state': relations.CHANGE_CREDENTIALS_TASK_STATE.PROCESSED,
                                                       'comment': '',
                                                       'old_email': self.accounts[0].email,
                                                       'new_email': 'new-email-1@xxx.yyy',
                                                       'new_nick': 'new-nick-1'}),
                               ('change_credentials', {'created_at': tasks[2].created_at,
                                                       'updated_at': tasks[2].updated_at,
                                                       'state': relations.CHANGE_CREDENTIALS_TASK_STATE.WAITING,
                                                       'comment': '',
                                                       'old_email': self.accounts[0].email,
                                                       'new_email': 'new-email-3@xxx.yyy',
                                                       'new_nick': 'new-nick-3'})])

    def test_has_records__remove(self):

        tasks = self.prepair_data()

        data_protection.remove_change_credentials_data(self.accounts[0].id)

        report = data_protection.collect_change_credentials_data(self.accounts[0].id)

        self.assertCountEqual(report, [])

        report = data_protection.collect_change_credentials_data(self.accounts[1].id)

        self.assertCountEqual(report,
                              [('change_credentials', {'created_at': tasks[1].created_at,
                                                       'updated_at': tasks[1].updated_at,
                                                       'state': relations.CHANGE_CREDENTIALS_TASK_STATE.WAITING,
                                                       'comment': '',
                                                       'old_email': self.accounts[1].email,
                                                       'new_email': 'new-email-2@xxx.yyy',
                                                       'new_nick': 'new-nick-2'})])


class AccountDataTests(clans_helpers.ClansTestsMixin,
                       utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.accounts = [self.accounts_factory.create_account()
                         for _ in range(2)]

    def test_defaults(self):
        report = data_protection.collect_account_data(self.accounts[0].id)

        self.maxDiff = None

        self.assertCountEqual(report,
                              [('nick', self.accounts[0].nick_verbose),
                               ('description', ''),
                               ('last_news_remind_time', self.accounts[0].last_news_remind_time),
                               ('gender', game_relations.GENDER.MALE),
                               ('infinit_subscription', False),
                               ('subscription_end_at', self.accounts[0].premium_end_at),
                               ('subscription_expired_notification_send_at',self.accounts[0]._model.premium_expired_notification_send_at),
                               ('active_end_at', self.accounts[0].active_end_at),
                               ('ban_game_end_at', None),
                               ('ban_forum_end_at', None),
                               ('created_at', self.accounts[0].created_at),
                               ('updated_at', self.accounts[0].updated_at),
                               ('email', self.accounts[0].email),
                               ('personal_messages_subscription', True),
                               ('news_subscription', True),
                               ('referer_domain', None),
                               ('referer', None),
                               ('referral_of', None),
                               ('referrals_number', 0),
                               ('action_id', None)])

    def prepair_settings(self):
        form = forms.SettingsForm({'personal_messages_subscription': False,
                                   'news_subscription': False,
                                   'description': 'some.description',
                                   'gender': game_relations.GENDER.FEMALE,
                                   'accept_invites_from_clans': False})

        self.assertTrue(form.is_valid())

        self.accounts[0].update_settings(form)

    def test_settings__collect(self):
        self.prepair_settings()

        report = data_protection.collect_account_data(self.accounts[0].id)

        for record in [('description', 'some.description'),
                       ('gender', game_relations.GENDER.FEMALE),
                       ('personal_messages_subscription', False),
                       ('news_subscription', False)]:

            self.assertIn(record, report)

    def test_settings__remove(self):
        self.prepair_settings()

        data_protection.remove_account_data(self.accounts[0].id)

        report = data_protection.collect_account_data(self.accounts[0].id)

        for record in [('description', ''),
                       ('gender', game_relations.GENDER.MALE),
                       ('personal_messages_subscription', False),
                       ('news_subscription', False)]:

            self.assertIn(record, report)

    def prepair_premiums(self):
        self.accounts[0].prolong_premium(30)

        notified_at = datetime.datetime.now()

        self.accounts[0]._model.premium_expired_notification_send_at = notified_at
        self.accounts[0].save()

        return notified_at

    def test_premiums__collect(self):
        notified_at = self.prepair_premiums()

        report = data_protection.collect_account_data(self.accounts[0].id)

        for record in [('subscription_end_at', self.accounts[0].premium_end_at),
                       ('subscription_expired_notification_send_at', notified_at),
                       ('infinit_subscription', False)]:
            self.assertIn(record, report)

        self.accounts[0].permanent_purchases.insert(shop_relations.PERMANENT_PURCHASE_TYPE.INFINIT_SUBSCRIPTION)
        self.accounts[0].save()

        report = data_protection.collect_account_data(self.accounts[0].id)

        for record in [('infinit_subscription', True)]:
            self.assertIn(record, report)

    def test_premiums__remove(self):
        self.prepair_premiums()

        data_protection.remove_account_data(self.accounts[0].id)

        report = data_protection.collect_account_data(self.accounts[0].id)

        zero = datetime.datetime.fromtimestamp(0)

        for record in [('subscription_end_at', zero),
                       ('subscription_expired_notification_send_at', zero),
                       ('infinit_subscription', False)]:
            self.assertIn(record, report)

        self.accounts[0].permanent_purchases.insert(shop_relations.PERMANENT_PURCHASE_TYPE.INFINIT_SUBSCRIPTION)
        self.accounts[0].save()

        data_protection.remove_account_data(self.accounts[0].id)

        report = data_protection.collect_account_data(self.accounts[0].id)

        for record in [('infinit_subscription', False)]:
            self.assertIn(record, report)

    def prepair_bans(self):
        self.accounts[0].ban_forum(1)
        self.accounts[0].ban_game(2)

    def test_bans__collect(self):
        self.prepair_bans()

        report = data_protection.collect_account_data(self.accounts[0].id)

        self.assertTrue(self.accounts[0].ban_forum_end_at < self.accounts[0].ban_game_end_at)

        for record in [('ban_game_end_at', self.accounts[0].ban_game_end_at),
                       ('ban_forum_end_at', self.accounts[0].ban_forum_end_at)]:
            self.assertIn(record, report)

    def test_bans__remove(self):
        self.prepair_bans()

        data_protection.remove_account_data(self.accounts[0].id)

        report = data_protection.collect_account_data(self.accounts[0].id)

        for record in [('ban_game_end_at', None),
                       ('ban_forum_end_at', None)]:
            self.assertIn(record, report)

    def prepaier_registration(self):
        account_id = logic.register_user(nick='xx.yy',
                                         email='xx.yy@zzz',
                                         password='asdf',
                                         referer='https://xx.yyy/zzz.html',
                                         referral_of_id=self.accounts[0].id,
                                         action_id='promo-1')[1]

        logic.update_referrals_number(self.accounts[0].id)

        self.accounts[0].reload()

        return account_id

    def test_registration__collect(self):
        account_id = self.prepaier_registration()

        report = data_protection.collect_account_data(self.accounts[0].id)

        for record in [('referrals_number', 1)]:
            self.assertIn(record, report)

        report = data_protection.collect_account_data(account_id)

        for record in [('referrals_number', 0),
                       ('referer_domain', 'xx.yyy'),
                       ('referer', 'https://xx.yyy/zzz.html'),
                       ('referral_of', self.accounts[0].id),
                       ('action_id', 'promo-1')]:
            self.assertIn(record, report)

    def test_registration__remove(self):
        account_id = self.prepaier_registration()

        data_protection.remove_account_data(self.accounts[0].id)

        report = data_protection.collect_account_data(self.accounts[0].id)

        for record in [('referrals_number', 0)]:
            self.assertIn(record, report)

        data_protection.remove_account_data(account_id)

        report = data_protection.collect_account_data(account_id)

        for record in [('referrals_number', 0),
                       ('referer_domain', None),
                       ('referer', None),
                       ('referral_of', None),
                       ('action_id', None)]:
            self.assertIn(record, report)


class CollectFullDataTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.accounts = [self.accounts_factory.create_account()
                         for _ in range(2)]

    def test_all_collectors_called(self):

        with mock.patch('the_tale.accounts.data_protection.collect_account_data') as collect_account_data, \
             mock.patch('the_tale.accounts.data_protection.collect_might_data') as collect_might_data, \
             mock.patch('the_tale.accounts.data_protection.collect_reset_password_data') as collect_reset_password_data, \
             mock.patch('the_tale.accounts.data_protection.collect_change_credentials_data') as collect_change_credentials_data, \
             mock.patch('the_tale.accounts.friends.data_protection.collect_data') as friends_collect_data, \
             mock.patch('the_tale.accounts.third_party.data_protection.collect_data') as third_party_collect_data, \
             mock.patch('the_tale.game.heroes.data_protection.collect_data') as heroes_collect_data, \
             mock.patch('the_tale.finances.bank.data_protection.collect_data') as bank_collect_data, \
             mock.patch('the_tale.finances.xsolla.data_protection.collect_data') as xsolla_collect_data:
            data_protection.collect_full_data(self.accounts[0].id)

        for mock_call in [collect_account_data,
                          collect_might_data,
                          collect_reset_password_data,
                          collect_change_credentials_data,
                          friends_collect_data,
                          third_party_collect_data,
                          heroes_collect_data,
                          bank_collect_data,
                          xsolla_collect_data]:
            self.assertEqual(mock_call.call_args_list, [mock.call(self.accounts[0].id)])

    def test_all_collectors_processed(self):
        report = data_protection.collect_full_data(self.accounts[0].id)
        self.assertTrue(report)


class PostprocessValueTests(utils_testcase.TestCase):

    def test(self):
        test_time = datetime.datetime.now()

        data = {'a': test_time,
                'b': {'c': relations.AWARD_TYPE.STANDARD_MINOR},
                333: ['e', relations.AWARD_TYPE.STANDARD_MAJOR]}

        result = data_protection.postprocess_value(data)

        self.assertEqual(result,
                         {'a': test_time.isoformat(),
                          'b': {'c': relations.AWARD_TYPE.STANDARD_MINOR.text},
                          '333': ['e', relations.AWARD_TYPE.STANDARD_MAJOR.text]})


class FirstStepRemovingTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

    def test_success(self):
        self.assertEqual(self.account.email, 'test-user-1@test.com')

        old_password = self.account._model.password

        data_protection.first_step_removing(self.account)

        self.account.reload()

        self.assertGreater(self.account.removed_at,
                           datetime.datetime.now() - datetime.timedelta(seconds=1))
        self.assertEqual(self.account.email, None)
        self.assertNotEqual(self.account._model.password, old_password)

    def test_reset_sessions(self):

        account_2 = self.accounts_factory.create_account()

        client_1 = django_test_client.Client()
        client_2 = django_test_client.Client()
        client_3 = django_test_client.Client()

        self.request_login(self.account.email, client=client_1)
        self.request_login(self.account.email, client=client_2)
        self.request_login(account_2.email, client=client_3)

        self.check_logged_in(self.account, client=client_1)
        self.check_logged_in(self.account, client=client_2)
        self.check_logged_in(account_2, client=client_3)

        data_protection.first_step_removing(self.account)

        self.request_html('/', client=client_1)
        self.request_html('/', client=client_2)
        self.request_html('/', client=client_3)

        self.check_logged_out(client=client_1)
        self.check_logged_out(client=client_2)
        self.check_logged_in(client=client_3)


class IdsListTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

    def test(self):
        self.assertCountEqual(data_protection.ids_list(self.account),
                              [('the_tale', self.account.id),
                               ('tt_players_properties', self.account.id),
                               ('tt_personal_messages', self.account.id),
                               ('tt_discord', self.account.id)])


class RemoveDataTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.accounts = [self.accounts_factory.create_account()
                         for _ in range(2)]

        data_protection.first_step_removing(self.accounts[0])

    def test_first_call(self):

        with mock.patch('the_tale.accounts.data_protection.remove_account_data') as remove_account_data, \
             mock.patch('the_tale.accounts.data_protection.remove_might_data') as remove_might_data, \
             mock.patch('the_tale.accounts.data_protection.remove_reset_password_data') as remove_reset_password_data, \
             mock.patch('the_tale.accounts.data_protection.remove_change_credentials_data') as remove_change_credentials_data, \
             mock.patch('the_tale.accounts.friends.data_protection.remove_data') as friends_remove_data, \
             mock.patch('the_tale.accounts.third_party.data_protection.remove_data') as third_party_remove_data, \
             mock.patch('the_tale.game.heroes.data_protection.remove_data', mock.Mock(return_value=False)) as heroes_remove_data, \
             mock.patch('the_tale.finances.bank.data_protection.remove_data') as bank_remove_data, \
             mock.patch('the_tale.finances.shop.data_protection.remove_data') as shop_remove_data, \
             mock.patch('the_tale.finances.xsolla.data_protection.remove_data') as xsolla_remove_data:
            data_protection.remove_data(self.accounts[0].id)

        for mock_call in [remove_account_data,
                          remove_might_data,
                          remove_reset_password_data,
                          remove_change_credentials_data,
                          friends_remove_data,
                          third_party_remove_data,
                          bank_remove_data,
                          shop_remove_data,
                          xsolla_remove_data]:
            self.assertEqual(mock_call.call_count, 0)

        self.assertEqual(heroes_remove_data.call_args_list, [mock.call(self.accounts[0].id)])

    def test_second_call(self):

        with mock.patch('the_tale.accounts.data_protection.remove_account_data') as remove_account_data, \
             mock.patch('the_tale.accounts.data_protection.remove_might_data') as remove_might_data, \
             mock.patch('the_tale.accounts.data_protection.remove_reset_password_data') as remove_reset_password_data, \
             mock.patch('the_tale.accounts.data_protection.remove_change_credentials_data') as remove_change_credentials_data, \
             mock.patch('the_tale.accounts.friends.data_protection.remove_data') as friends_remove_data, \
             mock.patch('the_tale.accounts.third_party.data_protection.remove_data') as third_party_remove_data, \
             mock.patch('the_tale.game.heroes.data_protection.remove_data', mock.Mock(return_value=True)) as heroes_remove_data, \
             mock.patch('the_tale.finances.bank.data_protection.remove_data') as bank_remove_data, \
             mock.patch('the_tale.finances.shop.data_protection.remove_data') as shop_remove_data, \
             mock.patch('the_tale.finances.xsolla.data_protection.remove_data') as xsolla_remove_data:
            data_protection.remove_data(self.accounts[0].id)

        for mock_call in [heroes_remove_data,
                          remove_account_data,
                          remove_might_data,
                          remove_reset_password_data,
                          remove_change_credentials_data,
                          friends_remove_data,
                          third_party_remove_data,
                          bank_remove_data,
                          shop_remove_data,
                          xsolla_remove_data]:
            self.assertEqual(mock_call.call_args_list, [mock.call(self.accounts[0].id)])

    def test_all_removers_processed(self):
        data_protection.remove_data(self.accounts[0].id)

        with mock.patch('the_tale.game.heroes.data_protection.remove_data', mock.Mock(return_value=True)):
            data_protection.remove_data(self.accounts[0].id)
